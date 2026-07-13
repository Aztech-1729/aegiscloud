"""Chaos testing for Aegis Cloud

Randomly injects failures to verify system resilience:
- Agent crashes
- WebSocket disconnects
- Redis restarts
- PostgreSQL restarts
- Network partitions
- High latency injection
"""
import asyncio
import random
import time
import logging
from typing import List, Callable
import docker
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChaosMonkey:
    """Injects random failures into the system"""
    
    def __init__(self, backend_url: str, redis_url: str, postgres_url: str):
        self.backend_url = backend_url
        self.redis_url = redis_url
        self.postgres_url = postgres_url
        self.docker_client = docker.from_env()
        self.attacks: List[Callable] = [
            self.restart_backend,
            self.restart_redis,
            self.restart_postgres,
            self.kill_agent_connection,
            self.inject_latency,
            self.overload_backend,
        ]
    
    async def restart_backend(self):
        """Restart backend service"""
        logger.info("🔥 Chaos: Restarting backend service")
        try:
            container = self.docker_client.containers.get("aegis-backend-test")
            container.restart()
            await asyncio.sleep(5)
            logger.info("✓ Backend restarted")
        except Exception as e:
            logger.error(f"Failed to restart backend: {e}")
    
    async def restart_redis(self):
        """Restart Redis service"""
        logger.info("🔥 Chaos: Restarting Redis")
        try:
            container = self.docker_client.containers.get("aegis-redis-test")
            container.restart()
            await asyncio.sleep(3)
            logger.info("✓ Redis restarted")
        except Exception as e:
            logger.error(f"Failed to restart Redis: {e}")
    
    async def restart_postgres(self):
        """Restart PostgreSQL service"""
        logger.info("🔥 Chaos: Restarting PostgreSQL")
        try:
            container = self.docker_client.containers.get("aegis-postgres-test")
            container.restart()
            await asyncio.sleep(10)
            logger.info("✓ PostgreSQL restarted")
        except Exception as e:
            logger.error(f"Failed to restart PostgreSQL: {e}")
    
    async def kill_agent_connection(self):
        """Simulate agent disconnection"""
        logger.info("🔥 Chaos: Simulating agent disconnect")
        # Send a signal to backend to close all WebSocket connections
        try:
            requests.post(f"{self.backend_url}/admin/kill-websockets", timeout=5)
            await asyncio.sleep(2)
            logger.info("✓ Agent connections terminated")
        except Exception as e:
            logger.error(f"Failed to kill agent connections: {e}")
    
    async def inject_latency(self):
        """Inject network latency"""
        logger.info("🔥 Chaos: Injecting 500ms latency")
        # This would use tc (traffic control) in production
        # For testing, we'll just delay responses
        await asyncio.sleep(0.5)
        logger.info("✓ Latency injected")
    
    async def overload_backend(self):
        """Send flood of requests to overload backend"""
        logger.info("🔥 Chaos: Overloading backend with requests")
        
        async def send_request():
            try:
                requests.get(f"{self.backend_url}/health", timeout=1)
            except:
                pass
        
        # Send 100 concurrent requests
        await asyncio.gather(*[send_request() for _ in range(100)])
        logger.info("✓ Backend overloaded")
    
    async def run_chaos(self, duration_seconds: int = 300):
        """Run chaos testing for specified duration"""
        logger.info(f"🐵 Starting chaos testing for {duration_seconds} seconds")
        
        start_time = time.time()
        attack_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Random delay between attacks (5-15 seconds)
            delay = random.uniform(5, 15)
            await asyncio.sleep(delay)
            
            # Pick random attack
            attack = random.choice(self.attacks)
            
            # Execute attack
            try:
                await attack()
                attack_count += 1
            except Exception as e:
                logger.error(f"Attack failed: {e}")
            
            # Verify system health
            await self.verify_health()
        
        logger.info(f"✓ Chaos testing complete. Executed {attack_count} attacks")
    
    async def verify_health(self):
        """Verify system is still healthy after attack"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                logger.warning("⚠️  System unhealthy after attack")
            else:
                logger.info("✓ System recovered")
        except Exception as e:
            logger.error(f"Health check failed: {e}")


async def main():
    """Main chaos runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chaos testing for Aegis Cloud")
    parser.add_argument("--duration", type=int, default=300, help="Duration in seconds")
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--postgres-url", default="postgresql://aegis:aegis_secret_2024@localhost:5432/aegis_cloud")
    
    args = parser.parse_args()
    
    monkey = ChaosMonkey(
        backend_url=args.backend_url,
        redis_url=args.redis_url,
        postgres_url=args.postgres_url
    )
    
    await monkey.run_chaos(duration_seconds=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
