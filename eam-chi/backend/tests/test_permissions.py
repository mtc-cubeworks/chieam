"""
Integration tests for permission enforcement.
Tests RBAC functionality including role-based permissions and sidebar access.

Run with: python -m pytest tests/test_permissions.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import fastapi_app

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture(scope="function")
async def client():
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestPermissionMatrix:
    """Tests for the permission matrix API."""
    
    async def test_get_permission_matrix(self, client: AsyncClient):
        """Test fetching the permission matrix."""
        response = await client.get("/api/admin/permissions/matrix")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "entities" in data["data"]
        assert "matrix" in data["data"]
        
        # Verify matrix structure
        matrix = data["data"]["matrix"]
        assert len(matrix) > 0
        
        for role_entry in matrix:
            assert "role_id" in role_entry
            assert "role_name" in role_entry
            assert "entities" in role_entry
            
            # Verify each entity has all permission fields including in_sidebar
            for entity_name, perms in role_entry["entities"].items():
                assert "can_read" in perms
                assert "can_create" in perms
                assert "can_update" in perms
                assert "can_delete" in perms
                assert "in_sidebar" in perms, f"in_sidebar missing for {entity_name}"
    
    async def test_permission_matrix_has_in_sidebar(self, client: AsyncClient):
        """Test that permission matrix includes in_sidebar field for all entities."""
        response = await client.get("/api/admin/permissions/matrix")
        data = response.json()
        
        # Check all roles have in_sidebar for all entities
        for role_entry in data["data"]["matrix"]:
            for entity_name, perms in role_entry["entities"].items():
                assert isinstance(perms.get("in_sidebar"), bool), \
                    f"in_sidebar should be boolean for {role_entry['role_name']}/{entity_name}"


class TestRoleManagement:
    """Tests for role management API."""
    
    async def test_list_roles(self, client: AsyncClient):
        """Test listing all roles."""
        response = await client.get("/api/admin/roles")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Verify role structure
        for role in data["data"]:
            assert "id" in role
            assert "name" in role
            assert "permissions" in role
            
            # Verify permissions include in_sidebar
            for perm in role["permissions"]:
                assert "in_sidebar" in perm, f"in_sidebar missing in permission for role {role['name']}"
    
    async def test_system_manager_has_full_access(self, client: AsyncClient):
        """Test that SystemManager role has full access to all entities."""
        response = await client.get("/api/admin/permissions/matrix")
        data = response.json()
        
        system_manager_found = False
        for role_entry in data["data"]["matrix"]:
            if role_entry["role_name"] == "SystemManager":
                system_manager_found = True
                for entity_name, perms in role_entry["entities"].items():
                    assert perms["can_read"] == True, f"SystemManager should have read access to {entity_name}"
                    assert perms["can_create"] == True, f"SystemManager should have create access to {entity_name}"
                    assert perms["can_update"] == True, f"SystemManager should have update access to {entity_name}"
                    assert perms["can_delete"] == True, f"SystemManager should have delete access to {entity_name}"
                break
        
        assert system_manager_found, "SystemManager role not found in matrix"


class TestEntityAccess:
    """Tests for entity-level access control."""
    
    async def test_todo_list_access(self, client: AsyncClient):
        """Test that todo list endpoint is accessible."""
        response = await client.get("/api/todo/list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
    
    async def test_meta_endpoint(self, client: AsyncClient):
        """Test that meta endpoint returns entity information."""
        response = await client.get("/api/meta")
        assert response.status_code == 200
        
        data = response.json()
        assert "entities" in data
        assert len(data["entities"]) > 0
        
        # Verify entities have required fields
        for entity in data["entities"]:
            assert "name" in entity
            assert "label" in entity
            assert "module" in entity
    
    async def test_entity_meta_detail(self, client: AsyncClient):
        """Test getting detailed metadata for a specific entity."""
        response = await client.get("/api/meta/todo")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert data["name"] == "todo"
        assert "fields" in data


class TestAdminUsers:
    """Tests for admin user management."""
    
    async def test_list_users(self, client: AsyncClient):
        """Test listing all users."""
        response = await client.get("/api/admin/users")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        
        # Should have at least the admin user
        assert len(data["data"]) > 0
        
        # Verify user structure
        for user in data["data"]:
            assert "id" in user
            assert "username" in user
            assert "email" in user


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
