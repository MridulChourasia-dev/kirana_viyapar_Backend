# Offline Sync — Quick Implementation Guide

## Files Created

| File | Purpose |
|------|---------|
| `db/types.ts` | TypeScript types for offline entities and sync queue |
| `db/database.ts` | SQLite database layer with schema management |
| `db/syncQueueManager.ts` | Manage pending operations and their lifecycle |
| `db/dataSyncService.ts` | Orchestrate sync with server and conflict resolution |
| `db/networkConnectivityManager.ts` | Monitor network state and trigger auto-sync |
| `store/customerStore.ts` | **UPDATED** — Now supports offline operations |

---

## Quick Start

### 1. Install Dependencies

```bash
npm install expo-sqlite expo-network uuid
```

### 2. Initialize in App Root (App.tsx)

```typescript
import { useCustomerStore } from './store/customerStore';

export default function App() {
  React.useEffect(() => {
    // Initialize offline sync on app startup
    useCustomerStore.getState().initialize();
  }, []);

  return <AppNavigator isAuthenticated={isAuthenticated} />;
}
```

### 3. Display Connectivity Status (Optional)

```typescript
function ConnectivityIndicator() {
  const { isOnline, pendingCount } = useCustomerStore();

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <Text>{isOnline ? '🟢 Online' : '🔴 Offline'}</Text>
      {pendingCount > 0 && (
        <Text style={{ marginLeft: 8 }}>
          📋 {pendingCount} pending sync
        </Text>
      )}
    </View>
  );
}
```

### 4. Use Stores as Usual

The stores now handle offline automatically:

```typescript
// Create customer (works offline)
await customerStore.createCustomer({ name: 'John' });

// Update customer (works offline)
await customerStore.updateCustomer(id, { phone: '...' });

// Delete customer (works offline)
await customerStore.deleteCustomer(id);

// Fetch customers (uses local cache if offline)
await customerStore.fetchCustomers(1);
```

**What happens:**
- ✅ Data saved to local SQLite immediately
- ✅ Operation queued if offline
- ✅ Auto-synced when device comes online
- ✅ Retried automatically on network errors
- ✅ Conflicts detected and can be resolved

---

## Store Integration Pattern

All stores (customers, products, invoices, payments) follow this pattern:

```typescript
initialize: async () => {
  await offlineDb.initialize();
  await networkConnectivityManager.initialize();
  
  // Listen for connectivity changes
  networkConnectivityManager.subscribe((isOnline) => {
    set({ isOnline });
  });
  
  // Listen for sync status
  syncQueueManager.subscribe((stats) => {
    set({ pendingCount: stats.total_pending });
  });
}
```

---

## API Routes Created

### Payments API (Backend)

**POST /api/v1/payments/**
- Create a payment (now integrated with offline queue on mobile)

**GET /api/v1/payments/invoice/{invoice_id}**
- List payments for an invoice

**GET /api/v1/payments/customer/{customer_id}**
- Get customer balance and payment history

---

## Offline Sync Sequence

```
User Action (Offline)
    ↓
Save to SQLite + Queue operation
    ↓
Update local UI immediately
    ↓
Network comes online
    ↓
Auto-detect: device online
    ↓
dataSyncService.startSync()
    ↓
For each queued item:
  - POST/PATCH/DELETE to server
  - Update local DB with response
  - Mark as synced or retry
    ↓
Conflict detected?
  - Store conflict data
  - Wait for user resolution (or auto-apply strategy)
    ↓
Sync complete: queue cleaned up
```

---

## Conflict Resolution

If a conflict is detected during sync:

```typescript
// Automatic (server_wins strategy)
await dataSyncService.resolveConflict(itemId, 'server_wins');

// Or let user choose
showConflictDialog({
  onServerWins: () => dataSyncService.resolveConflict(itemId, 'server_wins'),
  onClientWins: () => dataSyncService.resolveConflict(itemId, 'client_wins'),
  onMerge: () => dataSyncService.resolveConflict(itemId, 'merge'),
});
```

Available strategies:
- `server_wins` — Accept all server data (safest)
- `client_wins` — Keep local changes
- `last_write_wins` — Use most recent version
- `merge` — Intelligently combine both versions

---

## Monitoring Sync

### Subscribe to Sync Status

```typescript
import { dataSyncService } from './db/dataSyncService';

dataSyncService.subscribeSyncStatus((status) => {
  if (status === 'syncing') {
    console.log('🔄 Syncing...');
  } else if (status === 'idle') {
    console.log('✓ Sync complete');
  } else if (status === 'error') {
    console.log('✗ Sync error');
  }
});
```

### Get Sync Statistics

```typescript
import { syncQueueManager } from './db/syncQueueManager';

const stats = await syncQueueManager.getSyncStats();
console.log(`Pending: ${stats.total_pending}`);
console.log(`Synced: ${stats.total_synced}`);
console.log(`Failed: ${stats.total_failed}`);
console.log(`Conflicts: ${stats.total_conflicts}`);
```

---

## Manual Sync Trigger

```typescript
import { networkConnectivityManager } from './db/networkConnectivityManager';

// Manually trigger sync (e.g., from "Sync Now" button)
await networkConnectivityManager.triggerSync();
```

---

## Apply to Other Stores

To add offline support to other stores (products, invoices, payments):

1. **Import offline utilities:**
   ```typescript
   import { offlineDb } from '../db/database';
   import { syncQueueManager } from '../db/syncQueueManager';
   import { networkConnectivityManager } from '../db/networkConnectivityManager';
   ```

2. **Add state fields:**
   ```typescript
   interface State {
     // ... existing fields
     isOnline: boolean;
     pendingCount: number;
     initialize: () => Promise<void>;
   }
   ```

3. **Update CRUD operations:**
   - **CREATE:** Save to DB + queue + try server
   - **READ:** Try server → fallback to local cache
   - **UPDATE:** Update local + queue + try server
   - **DELETE:** Soft-delete + queue + try server

4. **See:** `customerStore.ts` for full example

---

## Testing

### Manual Testing Script

```typescript
async function testOfflineSync() {
  // 1. Go offline (toggle airplane mode)
  console.log('📴 Going offline...');

  // 2. Create customer
  const success = await customerStore.createCustomer({
    name: 'Test Customer',
    phone: '+91-9876543210',
  });
  console.log('✓ Customer created locally:', success);

  // 3. Verify queued
  const pending = await syncQueueManager.getPendingOperations();
  console.log('📋 Pending operations:', pending.length);

  // 4. Go online
  console.log('🟢 Going online...');

  // 5. Auto-sync should trigger
  await new Promise(r => setTimeout(r, 2000));

  // 6. Verify synced
  const remaining = await syncQueueManager.getPendingOperations();
  console.log('✓ After sync, pending:', remaining.length);
}
```

---

## Performance Notes

- **Storage:** SQLite can handle millions of records
- **Sync Batch:** Processes up to 50 pending items per sync cycle
- **Network Polling:** Checks every 5 seconds (customizable)
- **Queue Cleanup:** Synced items removed immediately

---

## Troubleshooting

### Issue: App crashes on offline DB operations
- **Fix:** Ensure `await offlineDb.initialize()` called once
- **Prevention:** Call in app root `useEffect`

### Issue: Sync never triggers when going online
- **Fix:** Check network connectivity with:
  ```typescript
  import * as NetInfo from 'expo-network';
  const state = await NetInfo.getNetworkStateAsync();
  console.log('Connected:', state.isConnected);
  ```

### Issue: Operations stuck in "syncing" state
- **Fix:** Server may have crashed; restart app to retry
- **Improvement:** Add watchdog timer to detect hung syncs

### Issue: Conflicts happening for every sync
- **Fix:** Ensure `server_version` field sent by server
- **Check:** Response contains all expected fields

---

## Documentation

Full architecture guide: [`OFFLINE_SYNC_ARCHITECTURE.md`](./OFFLINE_SYNC_ARCHITECTURE.md)

Covers:
- System design and data flow
- Schema definitions
- Conflict resolution strategies
- Error handling and resilience
- Future enhancements
