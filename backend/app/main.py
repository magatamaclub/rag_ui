from fastapi import FastAPI
from app.api import router as api_router
from app.database import init_database
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG UI Backend",
    description="Backend API for RAG UI with Dify Integration",
    version="1.0.0",
    debug=settings.APP_DEBUG,
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("🚀 Starting RAG UI Backend...")
    try:
        # Initialize database tables
        init_database()
        logger.info("✅ Application startup completed successfully")
    except Exception as e:
        logger.warning("⚠️ Database initialization failed: %s", e)
        logger.warning("🔄 Application will continue without database tables")
        logger.warning("📝 You may need to initialize the database manually")


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World"}
