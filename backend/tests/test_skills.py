"""Unit tests for skills engine"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.skills.engine import skill_engine
from app.models.models import User, Device
from app.core.security import hash_password


class TestSkillListing:
    """Tests for skill listing"""

    def test_list_all_skills(self):
        """Test listing all skills"""
        skills = skill_engine.list_skills()
        assert len(skills) > 0
        assert any(s["id"] == "gaming-optimization" for s in skills)
        assert any(s["id"] == "windows-repair" for s in skills)

    def test_list_skills_by_category(self):
        """Test filtering skills by category"""
        gaming_skills = skill_engine.list_skills(category="gaming")
        assert all(s["category"] == "gaming" for s in gaming_skills)
        assert len(gaming_skills) > 0

    def test_list_skills_by_search(self):
        """Test searching skills"""
        cleanup_skills = skill_engine.list_skills(search="cleanup")
        assert len(cleanup_skills) > 0
        assert any("cleanup" in s["name"].lower() or "cleanup" in s["description"].lower() 
                   for s in cleanup_skills)

    def test_get_skill_categories(self):
        """Test getting skill categories"""
        categories = skill_engine.get_skill_categories()
        assert len(categories) > 0
        assert any(c["name"] == "gaming" for c in categories)
        assert any(c["name"] == "maintenance" for c in categories)


class TestSkillExecution:
    """Tests for skill execution"""

    async def test_get_skill_details(self):
        """Test getting skill details"""
        skill = skill_engine.get_skill("gaming-optimization")
        assert skill is not None
        assert skill["name"] == "Gaming Optimization"
        assert len(skill["steps"]) > 0

    async def test_execute_skill_invalid(self, db_session: AsyncSession):
        """Test executing non-existent skill"""
        # Create test user and device
        user = User(
            email="skill_test@example.com",
            name="Skill Test User",
            password_hash=hash_password("password123"),
            plan="pro"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Skill Test Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        with pytest.raises(ValueError, match="Skill not found"):
            await skill_engine.execute_skill(
                db=db_session,
                user_id=user.id,
                device_id=device.id,
                skill_id="nonexistent-skill",
                user_plan="pro"
            )

    async def test_skill_plan_access(self, db_session: AsyncSession):
        """Test skill execution respects plan access"""
        # Create test user on free plan
        user = User(
            email="free_plan@example.com",
            name="Free Plan User",
            password_hash=hash_password("password123"),
            plan="free"
        )
        db_session.add(user)
        await db_session.flush()
        
        device = Device(
            user_id=user.id,
            name="Free Plan Device",
            device_token=f"test_token_{uuid.uuid4()}",
            status="online"
        )
        db_session.add(device)
        await db_session.flush()
        
        # Try to execute skill that requires pro plan
        result = await skill_engine.execute_skill(
            db=db_session,
            user_id=user.id,
            device_id=device.id,
            skill_id="gaming-optimization",
            user_plan="free"
        )
        
        # Some tools should be blocked
        blocked_tools = [s for s in result["steps"] if s.get("status") == "blocked"]
        assert len(blocked_tools) > 0


class TestSkillSteps:
    """Tests for skill step definitions"""

    def test_gaming_optimization_steps(self):
        """Test gaming optimization skill has correct steps"""
        skill = skill_engine.get_skill("gaming-optimization")
        assert skill is not None
        
        tool_names = [step["tool"] for step in skill["steps"]]
        assert "clean_temp" in tool_names
        assert "flush_dns" in tool_names
        assert "list_startup" in tool_names

    def test_windows_repair_steps(self):
        """Test windows repair skill has correct steps"""
        skill = skill_engine.get_skill("windows-repair")
        assert skill is not None
        
        tool_names = [step["tool"] for step in skill["steps"]]
        assert "run_sfc" in tool_names
        assert "run_dism" in tool_names
        assert "flush_dns" in tool_names

    def test_security_audit_steps(self):
        """Test security audit skill has correct steps"""
        skill = skill_engine.get_skill("security-audit")
        assert skill is not None
        
        tool_names = [step["tool"] for step in skill["steps"]]
        assert "defender_status" in tool_names
        assert "firewall_status" in tool_names
        assert "list_processes" in tool_names
