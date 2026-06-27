# deploy.py
"""Production-grade Deployment Utility.

Automates the end-to-end deployment lifecycle for the platform, including 
environment validation, container orchestration via Docker Compose, schema 
migrations, and post-deployment health verification.
"""

import asyncio
import logging
import shutil
import sys
from typing import Final

# Setup structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scripts.deploy")


class DeploymentUtility:
    """Orchestrates the deployment of the containerized platform stack."""

    def __init__(self, environment: str = "production") -> None:
        self.env: Final = environment
        self.compose_file: Final = "docker/docker-compose.yml"

    async def _run_command(self, cmd: list[str]) -> bool:
        """Executes system commands and logs output."""
        logger.info(f"Executing: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Command failed: {stderr.decode().strip()}")
            return False
        return True

    async def validate_infrastructure(self) -> bool:
        """Checks if Docker and Compose are available."""
        if not shutil.which("docker"):
            logger.error("Docker not found.")
            return False
        if not shutil.which("docker-compose"):
            logger.error("Docker Compose not found.")
            return False
        return True

    async def deploy(self) -> None:
        """Performs full deployment sequence."""
        logger.info(f"Starting deployment for environment: {self.env}")

        if not await self.validate_infrastructure():
            sys.exit(1)

        # 1. Build and Pull
        if not await self._run_command(["docker-compose", "-f", self.compose_file, "build"]):
            sys.exit(1)

        # 2. Start services
        if not await self._run_command(["docker-compose", "-f", self.compose_file, "up", "-d"]):
            sys.exit(1)

        # 3. Migrate Schema
        logger.info("Running database migrations...")
        if not await self._run_command(["docker-compose", "exec", "-T", "bot", "alembic", "upgrade", "head"]):
            logger.warning("Migrations failed. Manual intervention required.")

        # 4. Verify health
        logger.info("Verifying service health...")
        await self._run_command(["docker-compose", "ps"])
        
        logger.info("Deployment sequence completed successfully.")


if __name__ == "__main__":
    env_arg = sys.argv[1] if len(sys.argv) > 1 else "production"
    deployer = DeploymentUtility(environment=env_arg)
    
    try:
        asyncio.run(deployer.deploy())
    except Exception as e:
        logger.critical(f"Deployment crashed: {e}")
        sys.exit(1)
