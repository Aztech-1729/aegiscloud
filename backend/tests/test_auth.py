"""Unit tests for authentication endpoints"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db
from app.core.security import hash_password, verify_password


@pytest.fixture
async def client():
    """Test client with database override"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """Database session for tests"""
    async with get_db() as session:
        yield session


class TestUserRegistration:
    """Tests for user registration"""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email"""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "securepassword123",
                "name": "Test User"
            }
        )
        
        # Second registration with same email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "securepassword123",
                "name": "Test User 2"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too short
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepassword123",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """Tests for user login"""

    async def test_login_success(self, client: AsyncClient):
        """Test successful login"""
        # Register user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "securepassword123",
                "name": "Login User"
            }
        )
        
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password"""
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "correctpassword",
                "name": "Test User"
            }
        )
        
        # Try wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401


class TestPasswordHashing:
    """Tests for password hashing"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False


class TestTokenRefresh:
    """Tests for token refresh"""

    async def test_refresh_token_success(self, client: AsyncClient):
        """Test successful token refresh"""
        # Register and login
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "securepassword123",
                "name": "Test User"
            }
        )
        
        refresh_token = register_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )
        
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests for protected endpoints"""

    async def test_get_me_authenticated(self, client: AsyncClient):
        """Test /auth/me with valid token"""
        # Register and get token
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "protected@example.com",
                "password": "securepassword123",
                "name": "Test User"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # Access protected endpoint
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "protected@example.com"
        assert data["name"] == "Test User"

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Test /auth/me without token"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test /auth/me with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
