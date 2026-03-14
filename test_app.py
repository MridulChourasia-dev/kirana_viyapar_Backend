#!/usr/bin/env python
"""Quick test to verify app configuration and startup"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_app():
    print("Testing app import and configuration...")
    
    try:
        # Test imports
        from app.main import app
        from app.core.config import settings
        from app.db.session import engine, AsyncSessionLocal
        print("✓ All imports successful")
        
        # Test settings
        print(f"✓ Project: {settings.PROJECT_NAME}")
        print(f"✓ Database URL: {settings.ASYNC_DATABASE_URL}")
        print(f"✓ API V1 path: {settings.API_V1_STR}")
        print(f"✓ JWT Algorithm: {settings.JWT_ALGORITHM}")
        
        # Test routers
        from app.api.v1.router import api_router
        routes = [route.path for route in api_router.routes]
        print(f"✓ Routers registered: {len(routes)} routes")
        
        # Test models
        from app.models import User, Business, Customer, Product, Invoice, Payment
        print(f"✓ All models imported successfully")
        
        # Test DB connection (won't actually connect without DB, just test config)
        print(f"✓ Engine configured: {engine}")
        
        print("\n✅ All tests passed! App is ready to run with:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_app())
    sys.exit(0 if success else 1)
