#!/usr/bin/env python3
"""
Database initialization script for RAG UI Backend.
This script can be run independently to initialize the database.
"""

import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_database
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main initialization function."""
    logger.info("🔧 RAG UI Database Initialization Tool")
    logger.info(
        "Database URL: %s",
        settings.DATABASE_URL.replace(
            settings.DB_PASSWORD,
            "***",  # Hide password in logs
        ),
    )

    try:
        init_database()
        logger.info("🎉 Database initialization completed successfully!")
        return 0
    except Exception as e:
        logger.error("💥 Database initialization failed: %s", e)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
