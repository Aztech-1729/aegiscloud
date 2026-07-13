"""Load testing for Aegis Cloud using Locust

Simulates:
- 100 concurrent agents
- 1000 concurrent agents
- 10000 concurrent agents
- Command flood (1000 commands/sec)
- WebSocket burst (10K connections)
"""
from locust import HttpUser, task, between, events
import random
import time
import gevent
from gevent.pool import Group


class AegisAgent(HttpUser):
    """Simulates an Aegis Cloud agent"""
    
    wait_time = between(1, 5)
    
    def on_start(self):
        """Called when agent starts"""
        self.device_token = f"test_token_{random.randint(1000, 9999)}"
        self.device_id = None
    
    @task(10)
    def send_heartbeat(self):
        """Send heartbeat to server"""
        with self.client.post(
            "/api/v1/devices/heartbeat",
            json={
                "device_token": self.device_token,
                "cpu_usage": random.uniform(10, 90),
                "ram_usage": random.uniform(30, 80),
                "disk_usage": random.uniform(40, 70),
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Heartbeat failed: {response.status_code}")
    
    @task(3)
    def check_commands(self):
        """Check for pending commands"""
        with self.client.get(
            "/api/v1/commands/pending",
            headers={"Authorization": f"Bearer {self.device_token}"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                commands = response.json()
                if commands:
                    # Execute command
                    for cmd in commands:
                        self.execute_command(cmd["id"], cmd["tool_name"])
                response.success()
            else:
                response.failure(f"Command check failed: {response.status_code}")
    
    def execute_command(self, command_id: str, tool_name: str):
        """Execute a command"""
        self.client.post(
            f"/api/v1/commands/{command_id}/execute",
            json={"result": {"success": True, "data": "test"}},
            headers={"Authorization": f"Bearer {self.device_token}"}
        )
    
    @task(1)
    def get_system_info(self):
        """Get system info endpoint (read-heavy)"""
        self.client.get("/health")


class CommandFloodUser(HttpUser):
    """Simulates command flood - 1000 commands/sec"""
    
    wait_time = between(0.001, 0.01)
    
    def on_start(self):
        self.user_token = None
        # Register and login
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"loadtest_{random.randint(1000, 9999)}@example.com",
                "password": "password123",
                "name": "Load Test User"
            }
        )
        if response.status_code == 201:
            self.user_token = response.json()["access_token"]
    
    @task
    def create_command(self):
        """Create command rapidly"""
        if not self.user_token:
            return
        
        self.client.post(
            "/api/v1/commands",
            json={
                "device_id": "test-device-id",
                "tool_name": "system_info",
                "parameters": {}
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )


class WebSocketBurstUser(HttpUser):
    """Simulates WebSocket burst - 10K connections"""
    
    @task
    def connect_websocket(self):
        """Attempt WebSocket connection"""
        # Note: Locust doesn't natively support WebSocket
        # This would need to be implemented with websockets library
        pass


# Load test scenarios
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print(f"\n{'='*60}")
    print(f"Starting load test: {environment.runner.user_count} users")
    print(f"{'='*60}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print(f"\n{'='*60}")
    print(f"Load test complete")
    print(f"{'='*60}\n")


# Scenario configurations
SCENARIOS = {
    "100_agents": {
        "user_classes": [AegisAgent],
        "user_count": 100,
        "spawn_rate": 10,
        "duration": 300,
    },
    "1000_agents": {
        "user_classes": [AegisAgent],
        "user_count": 1000,
        "spawn_rate": 50,
        "duration": 600,
    },
    "10000_agents": {
        "user_classes": [AegisAgent],
        "user_count": 10000,
        "spawn_rate": 200,
        "duration": 900,
    },
    "command_flood": {
        "user_classes": [CommandFloodUser],
        "user_count": 100,
        "spawn_rate": 10,
        "duration": 60,
    },
}
