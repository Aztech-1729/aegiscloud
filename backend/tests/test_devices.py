"""Unit tests for device management"""
import pytest
from httpx import AsyncClient
import uuid

from app.main import app


@pytest.fixture
async def client():
    """Test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestDeviceCreation:
    """Tests for device creation"""

    async def test_create_device_success(self, client: AsyncClient):
        """Test successful device creation"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "device_test@example.com",
                "password": "securepassword123",
                "name": "Device Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create device
        response = await client.post(
            "/api/v1/devices",
            json={"name": "My Gaming PC"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Gaming PC"
        assert data["status"] == "offline"
        assert "id" in data
        assert "device_token" in data

    async def test_create_device_unauthenticated(self, client: AsyncClient):
        """Test device creation without authentication"""
        response = await client.post(
            "/api/v1/devices",
            json={"name": "Unauthorized Device"}
        )
        
        assert response.status_code == 401

    async def test_create_device_invalid_name(self, client: AsyncClient):
        """Test device creation with invalid name"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid_device@example.com",
                "password": "securepassword123",
                "name": "Invalid Device User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Try to create device with empty name
        response = await client.post(
            "/api/v1/devices",
            json={"name": ""},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 422


class TestDeviceListing:
    """Tests for device listing"""

    async def test_list_devices_empty(self, client: AsyncClient):
        """Test listing devices when none exist"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "empty_list@example.com",
                "password": "securepassword123",
                "name": "Empty List User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # List devices
        response = await client.get(
            "/api/v1/devices",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_list_devices_with_devices(self, client: AsyncClient):
        """Test listing devices when some exist"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "list_with_devices@example.com",
                "password": "securepassword123",
                "name": "List With Devices User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create 3 devices
        for i in range(3):
            await client.post(
                "/api/v1/devices",
                json={"name": f"Device {i}"},
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        # List devices
        response = await client.get(
            "/api/v1/devices",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestDeviceUpdates:
    """Tests for device updates"""

    async def test_rename_device(self, client: AsyncClient):
        """Test renaming a device"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "rename_test@example.com",
                "password": "securepassword123",
                "name": "Rename Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create device
        device_response = await client.post(
            "/api/v1/devices",
            json={"name": "Original Name"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        device_id = device_response.json()["id"]
        
        # Rename device
        response = await client.patch(
            f"/api/v1/devices/{device_id}",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    async def test_rename_device_unauthorized(self, client: AsyncClient):
        """Test renaming another user's device"""
        # Register user 1
        register1_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "password": "securepassword123",
                "name": "User 1"
            }
        )
        
        token1 = register1_response.json()["access_token"]
        
        # Create device as user 1
        device_response = await client.post(
            "/api/v1/devices",
            json={"name": "User 1 Device"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        device_id = device_response.json()["id"]
        
        # Register user 2
        register2_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "securepassword123",
                "name": "User 2"
            }
        )
        
        token2 = register2_response.json()["access_token"]
        
        # Try to rename user 1's device as user 2
        response = await client.patch(
            f"/api/v1/devices/{device_id}",
            json={"name": "Hacked Name"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 404


class TestDeviceDeletion:
    """Tests for device deletion"""

    async def test_delete_device(self, client: AsyncClient):
        """Test deleting a device"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "delete_test@example.com",
                "password": "securepassword123",
                "name": "Delete Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create device
        device_response = await client.post(
            "/api/v1/devices",
            json={"name": "To Be Deleted"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        device_id = device_response.json()["id"]
        
        # Delete device
        response = await client.delete(
            f"/api/v1/devices/{device_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify device is gone
        list_response = await client.get(
            "/api/v1/devices",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert len(list_response.json()) == 0

    async def test_delete_nonexistent_device(self, client: AsyncClient):
        """Test deleting a non-existent device"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "delete_nonexistent@example.com",
                "password": "securepassword123",
                "name": "Delete Nonexistent User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Try to delete non-existent device
        response = await client.delete(
            f"/api/v1/devices/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 404
