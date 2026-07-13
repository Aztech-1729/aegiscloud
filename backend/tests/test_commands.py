"""Unit tests for command execution"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.main import app
from app.db.session import get_db
from app.services.command_queue import CommandQueue
from app.services.tool_registry import tool_registry, ToolValidationError
from app.models.models import CommandStatus, CommandPriority


@pytest.fixture
async def client():
    """Test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """Database session"""
    async with get_db() as session:
        yield session


@pytest.fixture
def command_queue():
    """Command queue instance"""
    return CommandQueue()


class TestToolRegistry:
    """Tests for tool registry"""

    def test_tool_registry_initialized(self):
        """Test tool registry has tools"""
        tools = tool_registry.list_tools()
        assert len(tools) > 0
        assert any(t["name"] == "system_info" for t in tools)

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid input"""
        params = {"sort_by": "cpu", "limit": 20}
        validated = tool_registry.validate_parameters("list_processes", params)
        
        assert validated["sort_by"] == "cpu"
        assert validated["limit"] == 20

    def test_validate_parameters_invalid_type(self):
        """Test parameter validation with invalid type"""
        params = {"limit": "not-a-number"}
        
        with pytest.raises(ToolValidationError):
            tool_registry.validate_parameters("list_processes", params)

    def test_validate_parameters_missing_required(self):
        """Test parameter validation with missing required field"""
        params = {}  # Missing 'name' for kill_process
        
        with pytest.raises(ToolValidationError):
            tool_registry.validate_parameters("kill_process", params)

    def test_requires_approval(self):
        """Test approval requirement check"""
        # kill_process should require approval
        assert tool_registry.requires_approval("kill_process") is True
        
        # system_info should not require approval
        assert tool_registry.requires_approval("system_info") is False

    def test_risk_level(self):
        """Test risk level retrieval"""
        assert tool_registry.get_risk_level("kill_process") == "high"
        assert tool_registry.get_risk_level("system_info") == "low"

    def test_plan_access(self):
        """Test plan-based access control"""
        # Free plan should have access to basic tools
        assert tool_registry.is_allowed_on_plan("system_info", "free") is True
        
        # Free plan should NOT have access to advanced tools
        assert tool_registry.is_allowed_on_plan("storage_analysis", "free") is False
        
        # Pro plan should have access to advanced tools
        assert tool_registry.is_allowed_on_plan("storage_analysis", "pro") is True


class TestCommandQueue:
    """Tests for command queue"""

    async def test_enqueue_command(self, db_session, command_queue):
        """Test enqueuing a command"""
        # Create test user and device first
        from app.models.models import User, Device
        from app.core.security import hash_password
        
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
            plan="pro"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Test Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        # Enqueue command
        command = await command_queue.enqueue(
            db=db_session,
            user_id=user.id,
            device_id=device.id,
            tool_name="system_info",
            parameters={},
            user_plan="pro"
        )
        
        assert command.id is not None
        assert command.status == CommandStatus.queued
        assert command.tool_name == "system_info"
        assert command.nonce is not None

    async def test_enqueue_invalid_tool(self, db_session, command_queue):
        """Test enqueuing command with invalid tool"""
        from app.models.models import User, Device
        from app.core.security import hash_password
        
        user = User(
            email="test2@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
            plan="pro"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Test Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        with pytest.raises(ValueError, match="Unknown tool"):
            await command_queue.enqueue(
                db=db_session,
                user_id=user.id,
                device_id=device.id,
                tool_name="nonexistent_tool",
                parameters={},
                user_plan="pro"
            )

    async def test_mark_command_running(self, db_session, command_queue):
        """Test marking command as running"""
        from app.models.models import User, Device, Command
        from app.core.security import hash_password
        
        user = User(
            email="test3@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
            plan="pro"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Test Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        command = Command(
            user_id=user.id,
            device_id=device.id,
            tool_name="system_info",
            parameters={},
            status=CommandStatus.queued,
            nonce=uuid.uuid4().hex
        )
        db_session.add(command)
        await db_session.flush()
        
        await command_queue.mark_running(db_session, command.id)
        await db_session.refresh(command)
        
        assert command.status == CommandStatus.running
        assert command.started_at is not None

    async def test_mark_command_completed(self, db_session, command_queue):
        """Test marking command as completed"""
        from app.models.models import User, Device, Command
        from app.core.security import hash_password
        
        user = User(
            email="test4@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
            plan="pro"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Test Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        command = Command(
            user_id=user.id,
            device_id=device.id,
            tool_name="system_info",
            parameters={},
            status=CommandStatus.running,
            nonce=uuid.uuid4().hex
        )
        db_session.add(command)
        await db_session.flush()
        
        result = {"cpu_percent": 45.2, "ram_percent": 67.8}
        await command_queue.mark_completed(db_session, command.id, result)
        await db_session.refresh(command)
        
        assert command.status == CommandStatus.completed
        assert command.result == result
        assert command.completed_at is not None


class TestCommandAPI:
    """Tests for command API endpoints"""

    async def test_create_command(self, client: AsyncClient):
        """Test creating a command via API"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "api_test@example.com",
                "password": "securepassword123",
                "name": "API Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create device
        device_response = await client.post(
            "/api/v1/devices",
            json={"name": "API Test Device"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        device_id = device_response.json()["id"]
        
        # Create command
        response = await client.post(
            "/api/v1/commands",
            json={
                "device_id": device_id,
                "tool_name": "system_info",
                "parameters": {}
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["tool_name"] == "system_info"
        assert data["status"] == "queued"

    async def test_list_commands(self, client: AsyncClient):
        """Test listing commands"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "list_test@example.com",
                "password": "securepassword123",
                "name": "List Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # List commands
        response = await client.get(
            "/api/v1/commands",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_cancel_command(self, client: AsyncClient):
        """Test cancelling a command"""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "cancel_test@example.com",
                "password": "securepassword123",
                "name": "Cancel Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Create device
        device_response = await client.post(
            "/api/v1/devices",
            json={"name": "Cancel Test Device"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        device_id = device_response.json()["id"]
        
        # Create command
        command_response = await client.post(
            "/api/v1/commands",
            json={
                "device_id": device_id,
                "tool_name": "system_info",
                "parameters": {}
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        command_id = command_response.json()["id"]
        
        # Cancel command
        response = await client.post(
            f"/api/v1/commands/{command_id}/cancel",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
