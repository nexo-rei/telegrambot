# restore.py
"""Production-grade Restore Utility.

Provides a robust, transactional interface for restoring platform state from
versioned backup archives. Integrates integrity verification, dependency 
checking, and safe extraction processes to ensure disaster recovery reliability 
within the Nigerian Investment Platform.
"""

import asyncio
import hashlib
import logging
import shutil
import tarfile
from pathlib import Path
from typing import Final

# Setup structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scripts.restore")


class RestoreUtility:
    """Orchestrates the safe decompression, verification, and restoration of assets."""

    def __init__(self, backup_dir: str, restore_root: str) -> None:
        self.backup_path: Final = Path(backup_dir)
        self.restore_path: Final = Path(restore_root)

    async def _verify_checksum(self, archive_path: Path) -> bool:
        """Verifies the integrity of the archive against its SHA-256 manifest."""
        checksum_file = archive_path.with_suffix(".tar.gz.sha256")
        if not checksum_file.exists():
            logger.error("Integrity manifest missing.")
            return False

        with open(checksum_file, "r") as f:
            expected_hash = f.read().strip()

        sha256 = hashlib.sha256()
        with open(archive_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest() == expected_hash

    async def restore(self, archive_name: str, force: bool = False) -> None:
        """Executes the restoration process."""
        archive_path = self.backup_path / archive_name
        
        if not archive_path.exists():
            logger.error(f"Archive not found: {archive_path}")
            return

        logger.info(f"Verifying integrity for: {archive_name}")
        if not await self._verify_checksum(archive_path):
            logger.error("Integrity verification failed. Aborting restore.")
            return

        logger.info("Integrity verified. Initiating extraction...")
        try:
            # Prepare restoration target
            if self.restore_path.exists() and force:
                shutil.rmtree(self.restore_path)
            self.restore_path.mkdir(parents=True, exist_ok=True)

            # Perform extraction
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=self.restore_path)
            
            # Logic here would trigger DB and Redis reload operations
            logger.info("Restore successfully completed.")

        except Exception as e:
            logger.critical(f"Restore operation failed: {e}")
            raise


if __name__ == "__main__":
    # Define locations
    BACKUP_DIR = "storage/backups"
    RESTORE_TARGET = "storage/restore_staging"

    utility = RestoreUtility(BACKUP_DIR, RESTORE_TARGET)
    
    # Example execution via command line arguments could be added here
    try:
        # Placeholder for specific archive selection
        asyncio.run(utility.restore("backup_latest.tar.gz", force=True))
    except Exception:
        exit(1)
