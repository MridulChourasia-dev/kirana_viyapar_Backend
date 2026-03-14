# Offline Sync Architecture — Viyapar Mobile

## Overview

The Viyapar mobile app implements a robust offline-first architecture that enables seamless functionality when the device loses network connectivity. Data is stored locally in SQLite, and changes are automatically synced with the server when the device comes back online.

**Key Features:**
- ✓ Local SQLite database for offline data persistence
- ✓ Automatic sync queue for tracking pending operations
- ✓ Network connectivity detection and auto-sync triggers
- ✓ Conflict resolution strategies (server-wins, client-wins, merge, etc.)
- ✓ Exponential backoff retry logic with max attempt limits
- ✓ Seamless integration with existing Zustand stores

---

## Architecture Components

### 1. Local Database Layer (`db/database.ts`)

**Responsibility:** Manage all local SQLite data storage and retrieval.

**Features:**
- Creates and initializes the SQLite database on first app launch
- Maintains schema for all entities: customers, products, invoices, payments
- Provides CRUD operations for each entity type
- Tracks local creation flags and server versions for conflict detection

**Key Methods:**
```typescript
await offlineDb.initialize();                    // Initialize DB schema
await offlineDb.insertCustomer(customer);       // Save customer locally
const customers = await offlineDb.getAllCustomers();
await offlineDb.updateCustomer(id, updates);
await offlineDb.deleteCustomer(id);             // Soft delete with is_deleted flag
```

**Schema Highlights:**
- All entities include `created_locally` flag for sync origin detection
- `server_version` tracks data mutations for conflict resolution
- `is_deleted` flag enables soft-deletes (recoverable)
- Foreign key constraints (e.g., payments → invoices)

---

### 2. Sync Queue Manager (`db/syncQueueManager.ts`)

**Responsibility:** Track pending operations and manage their lifecycle through sync.

**Features:**
- Queue operations (create, update, delete) with priority levels
- Track attempt counts and errors for failed operations
- Manage conflict state and resolution

**Queue Item Lifecycle:**
```
pending → syncing → synced (removed from queue)
       ↓
    failed (retry up to max_attempts)
       ↓
    conflict (requires manual resolution)
```

**Key Methods:**
```typescript
await syncQueueManager.queueOperation('customer', 'create', id, payload, priority);
await syncQueueManager.markSyncing(id);
await syncQueueManager.markSynced(id);          // Success
await syncQueueManager.markFailed(id, error, shouldRetry);
await syncQueueManager.markConflict(id, conflictData);
await syncQueueManager.resolveConflict(id, strategy);
```

**Priority Levels:**
- `1` = HIGH (critical data, e.g., payments)
- `2` = NORMAL (standard updates)
- `3` = LOW (non-critical, e.g., notes)

---

### 3. Data Sync Service (`db/dataSyncService.ts`)

**Responsibility:** Execute the sync process; communicate with the server and resolve conflicts.

**Features:**
- Attempt to sync pending operations to the server
- Detect and handle conflicts with version comparison
- Update local entities with server responses
- Implement exponential backoff for retries

**Conflict Detection:**
```typescript
if (response.conflict) {
  // Server detected version mismatch
  conflictData = {
    local_version: item.payload.version,
    server_version: response.server_version,
    local_data: item.payload,
    server_data: response.data,
    resolution_strategy: 'server_wins'  // default
  }
}
```

**Conflict Resolution Strategies:**
- **server_wins**: Accept all server data (default for safety)
- **client_wins**: Keep local changes, discard server updates
- **last_write_wins**: Use the most recently modified version
- **merge**: Intelligently combine non-conflicting fields

**Key Methods:**
```typescript
await dataSyncService.startSync();              // Sync all pending ops
await dataSyncService.resolveConflict(itemId, 'server_wins');
await dataSyncService.pullLatestData('customer'); // Initial sync
```

**Retry Logic:**
- Requires successful HTTP response before marking as synced
- Retryable errors: 500+, 408, 429 (server-side issues)
- Non-retryable errors: 400, 401, 403, 404 (client-side issues)
- Max 5 attempts per operation before marking as failed
- Exponential backoff: 2^attempt_count seconds

---

### 4. Network Connectivity Manager (`db/networkConnectivityManager.ts`)

**Responsibility:** Monitor device network state and trigger auto-sync when online.

**Features:**
- Polling-based network state detection (every 5 seconds)
- Automatic sync trigger when device transitions from offline → online
- Listener pattern for connectivity state changes

**State Detection:**
```typescript
const isOnline = networkConnectivityManager.isDeviceOnline();  // boolean

// Subscribe to changes
networkConnectivityManager.subscribe((isOnline) => {
  if (isOnline) {
    console.log('🔄 Device online - triggering sync');
  } else {
    console.log('📴 Device offline - queuing operations');
  }
});
```

**Auto-Sync Trigger:**
When device detects online transition:
1. Emit connectivity changed event
2. Wait 1 second for network stabilization
3. Call `dataSyncService.startSync()`
4. Continue normal app operation

---

### 5. Integration with Stores (`store/customerStore.ts`)

**Pattern:** All data operations (CREATE, UPDATE, DELETE, READ) follow this flow:

```typescript
// Example: Create Customer
createCustomer: async (payload: CustomerCreate) => {
  // 1. Generate local ID and save to SQLite immediately
  const id = uuid();
  const customer = { id, ...payload, created_at: now };
  await offlineDb.insertCustomer(customer);

  // 2. Check network state
  if (isOnline) {
    try {
      // 3. Try to create on server
      await customerApi.create(payload);
      // Success - no queue entry needed
    } catch (err) {
      // 4a. Server error - queue for later retry
      await syncQueueManager.queueOperation('customer', 'create', id, payload, 1);
    }
  } else {
    // 4b. Offline - queue operation
    await syncQueueManager.queueOperation('customer', 'create', id, payload, 1);
  }

  // 5. Update UI from local data
  await get().fetchCustomers();
  return true;
}
```

**Read Flow:**
```typescript
fetchCustomers: async (page = 1) => {
  if (isOnline) {
    // Try server first, cache result locally
    const res = await customerApi.list(page);
    for (const customer of res.data) {
      await offlineDb.insertCustomer(customer);
    }
    setCustomers(res.data);
  } else {
    // Fall back to local cache
    const localCustomers = await offlineDb.getAllCustomers();
    setCustomers(localCustomers);
  }
}
```

---

## Data Flow Diagrams

### Offline → Online Transition
```
[Device Offline]
    ↓
  User creates/edits data locally
    ↓
  Operation queued + saved to SQLite
    ↓
[Network detected as Online]
    ↓
  NetworkConnectivityManager emits 'online' event
    ↓
  dataSyncService.startSync() called
    ↓
  For each pending operation:
    • markSyncing(id)
    • POST/PATCH/DELETE to server
    ↓
  If success → markSynced(id)
  If conflict → markConflict(id, conflictData)
  If error (retryable) → markFailed(id, error, true)
  If error (fatal) → markFailed(id, error, false)
    ↓
[All operations processed]
```

### Conflict Resolution Flow
```
[Sync detects version mismatch]
    ↓
  markConflict(id, {
    local_version: 2,
    server_version: 3,
    local_data: {...},
    server_data: {...}
  })
    ↓
[User notified of conflict]
    ↓
  User chooses resolution strategy:
    • "Use Server" (server_wins)
    • "Keep Mine" (client_wins)
    • "Merge"
    ↓
  resolveConflict(id, strategy)
    ↓
  Item re-queued with resolved data
    ↓
[Retry sync with resolved data]
```

---

## Implementation Guide

### Step 1: Initialize Offline Sync (App.tsx or Root Component)

```typescript
import { useCustomerStore } from './store/customerStore';

export default function App() {
  useEffect(() => {
    // Initialize offline support on app start
    useCustomerStore.getState().initialize();
  }, []);

  return <AppNavigator />;
}
```

### Step 2: Display Sync Status in UI

```typescript
function SyncStatusBadge() {
  const { isOnline, pendingCount } = useCustomerStore();
  
  return (
    <View>
      <Text>{isOnline ? '🟢 Online' : '🔴 Offline'}</Text>
      {pendingCount > 0 && <Text>⏳ {pendingCount} pending</Text>}
    </View>
  );
}
```

### Step 3: Handle Conflicts (Optional UI)

```typescript
function ConflictResolutionModal({ item }) {
  return (
    <Modal title="Conflict Detected">
      <Button 
        title="Use Server Version" 
        onPress={() => dataSyncService.resolveConflict(item.id, 'server_wins')}
      />
      <Button 
        title="Keep My Changes" 
        onPress={() => dataSyncService.resolveConflict(item.id, 'client_wins')}
      />
    </Modal>
  );
}
```

### Step 4: Manual Sync Trigger

```typescript
function ManualSyncButton() {
  return (
    <Button 
      title="Sync Now" 
      onPress={() => networkConnectivityManager.triggerSync()}
    />
  );
}
```

---

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  balance REAL,
  is_deleted INTEGER,
  server_version INTEGER,
  created_locally INTEGER,  -- 1 if created offline
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### Products Table
```sql
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  sku TEXT UNIQUE,
  sale_price REAL,
  is_deleted INTEGER,
  server_version INTEGER,
  created_locally INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### Sync Queue Table
```sql
CREATE TABLE sync_queue (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,        -- 'customer', 'product', etc.
  operation TEXT NOT NULL,          -- 'create', 'update', 'delete'
  entity_id TEXT NOT NULL,
  payload TEXT NOT NULL,            -- JSON stringified
  status TEXT DEFAULT 'pending',    -- 'pending', 'syncing', 'synced', 'failed', 'conflict'
  attempt_count INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 5,
  error TEXT,
  conflict_data TEXT,               -- JSON stringified ConflictData
  priority INTEGER DEFAULT 2,
  created_at TEXT NOT NULL,
  attempted_at TEXT
);
```

---

## Error Handling & Resilience

### Retry Strategy
- **Attempt 1:** Immediate
- **Attempt 2:** 2 seconds
- **Attempt 3:** 4 seconds
- **Attempt 4:** 8 seconds
- **Attempt 5:** 16 seconds
- After 5 failures: Mark as `failed`, require manual intervention

### Network Conditions Handled
- WiFi → Cellular switch ✓
- Airplane mode toggle ✓
- Intermittent packet loss ✓
- Server timeouts (408, 429) ✓
- Server errors (5xx) ✓
- Authentication failures (401) ✓

### Conflict Scenarios

**Scenario 1: Concurrent Edits**
- User edits customer locally while offline
- Server receives another edit from web app
- On sync, conflict detected
- Resolution: `server_wins` or merge strategy

**Scenario 2: Create After Delete**
- User deletes customer, goes offline
- Creates new customer with same name
- On sync, server rejects delete (entity not found)
- System handles gracefully

---

## Performance Considerations

- **SQLite Storage:** ~10-100 MB typical (millions of records possible)
- **Sync Queue:** Usually <100 items (most sync quickly)
- **Batch Sync:** Process up to 50 items per sync cycle
- **Network Polling:** 5-second interval (adjustable)
- **Automatic Cleanup:** Synced items removed from queue

---

## Testing Offline Support

### Manual Testing Checklist
- [ ] Create customer offline → verify in local DB
- [ ] Go online → verify auto-sync triggered
- [ ] Verify customer appears on server after sync
- [ ] Edit customer offline → queue verified
- [ ] Go online with queued edits → sync and verify
- [ ] Edit same entity from web + mobile (parallel) → resolution
- [ ] Simulate network failures (toggle airplane mode)

### Automated Test Example
```typescript
test('should queue operation when offline', async () => {
  // Mock network as offline
  vi.mock('../db/networkConnectivityManager', () => ({
    isDeviceOnline: () => false
  }));

  const store = useCustomerStore();
  await store.createCustomer({ name: 'Test' });

  // Verify in local DB
  const local = await offlineDb.getAllCustomers();
  expect(local).toHaveLength(1);

  // Verify in sync queue
  const pending = await syncQueueManager.getPendingOperations();
  expect(pending).toHaveLength(1);
  expect(pending[0].operation).toBe('create');
});
```

---

## Dependency Installation

Required packages (add to `package.json`):
```json
{
  "expo-sqlite": "^13.0+",
  "expo-network": "^5.0+",
  "uuid": "^9.0+"
}
```

Install via:
```bash
npm install expo-sqlite expo-network uuid
```

---

## Future Enhancements

1. **Selective Sync:** Allow users to choose which entities to sync
2. **Compression:** Compress queue payloads for large operations
3. **Analytics:** Track sync success rates, conflicts, latency
4. **Cache Expiry:** Auto-invalidate stale local data
5. **Encryption:** Encrypt sensitive data in SQLite
6. **Peer Sync:** Sync between multiple devices via server

---

## Troubleshooting

### Issue: Sync stuck in `syncing` state
- **Fix:** Manually clear queue or restart app
- **Root:** Network interrupted during sync

### Issue: Conflicts not resolving
- **Fix:** User must select resolution strategy
- **Root:** System cannot auto-merge conflicting changes

### Issue: Old data showing in offline mode
- **Fix:** Implement cache expiry (add `cached_at` timestamp)
- **Root:** Local cache stale after offline period

---

## References

- [Conflict-free Replicated Data Types (CRDTs)](https://crdt.tech/)
- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)
- [React Native Offline-First Patterns](https://www.npmjs.com/package/redux-persist)
