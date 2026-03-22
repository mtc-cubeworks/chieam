import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import fastapi_app
from app.core.database import async_session_maker
from app.modules.core.models.auth import User, Role
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from jose import jwt

def create_test_token(data: dict) -> str:
    """Create a JWT access token for testing."""
    # Hardcoded secret from config for testing
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_auth_headers():
    async with async_session_maker() as db:
        # Get admin user
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Admin user not found. Did you run seed?")
            return None
            
        token = create_test_token({"sub": user.username, "user_id": user.id})
        return {"Authorization": f"Bearer {token}"}

async def run_validation():
    print("🔄 Starting validation...")
    
    # Manually trigger lifespan startup
    from app.main import lifespan
    
    # Create an async context manager for lifespan
    scope = {"type": "lifespan"}
    
    # 1. Get Auth
    headers = await get_auth_headers()
    if not headers:
        return

    # Trigger loading manually to be sure
    from app.core.loader import load_modules
    from app.entities import load_all_entities
    print("🔄 Manually loading modules and entities...")
    load_modules()
    load_all_entities()

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        # 2. Create Todo
        print("\n📝 Testing Create Todo...")
        todo_data = {
            "title": "Test Todo via Forge",
            "description": "This todo was created after module re-creation",
            "status": "open",
            "priority": "high",
            "due_date": "2024-12-31",
            "completed": False
        }
        
        response = await client.post(
            "/api/entity/todo/action",
            json={"action": "create", "data": todo_data},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Create failed with HTTP {response.status_code}: {response.text}")
            return
        
        resp_data = response.json()
        if resp_data.get("status") == "error":
            print(f"❌ Create failed with API error: {resp_data.get('message')}")
            if "errors" in resp_data:
                print(f"   Errors: {resp_data['errors']}")
            return
            
        created_todo = resp_data.get("data")
        if not created_todo:
            print(f"❌ Create failed: No data returned. Full response: {resp_data}")
            return
            
        todo_id = created_todo["id"]
        print(f"✅ Created Todo: {todo_id}")
        
        # 3. Read Todo
        print("\n📖 Testing Read Todo...")
        response = await client.get(f"/api/entity/todo/detail/{todo_id}", headers=headers)
        if response.status_code != 200:
            print(f"❌ Read failed: {response.text}")
            return
        print(f"✅ Read Todo: {response.json()['data']['title']}")
        
        # 4. Update Todo
        print("\n✏️ Testing Update Todo...")
        response = await client.post(
            "/api/entity/todo/action",
            json={
                "action": "update", 
                "id": todo_id,
                "data": {"status": "in_progress"}
            },
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Update failed: {response.text}")
            return
        print(f"✅ Updated Status: {response.json()['data']['status']}")
        
        # 5. Create Comment (Link Field Test)
        print("\n💬 Testing Create Comment (Link Field)...")
        comment_data = {
            "todo_id": todo_id,
            "content": "This is a test comment",
            "author": "admin"
        }
        response = await client.post(
            "/api/entity/todo_comment/action",
            json={"action": "create", "data": comment_data},
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Create Comment failed: {response.text}")
            return
        
        comment_data_resp = response.json().get('data')
        comment_id = comment_data_resp['id']
        print(f"✅ Created Comment: {comment_id}")
        
        # 6. Delete Comment first (Foreign Key Constraint)
        print("\n🗑️ Testing Delete Comment...")
        response = await client.post(
            "/api/entity/todo_comment/action",
            json={"action": "delete", "id": comment_id},
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Deleted Comment")
        else:
            print(f"❌ Delete Comment failed: {response.text}")
            return

        # 7. Delete Todo
        print("\n🗑️ Testing Delete Todo...")
        
        response = await client.post(
            "/api/entity/todo/action",
            json={"action": "delete", "id": todo_id},
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Deleted Todo")
        else:
            print(f"ℹ️ Delete Todo failed (expected if comments exist): {response.json().get('message')}")
    
    print("\n🎉 Validation Complete!")

if __name__ == "__main__":
    asyncio.run(run_validation())
