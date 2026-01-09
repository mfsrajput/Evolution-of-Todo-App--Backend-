from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import settings
from app.config import settings

# Import routers
from app.auth.auth import router as auth_router
from app.todos.crud import router as todos_router
from app.database.database import engine, test_db_connection

app = FastAPI(
    title="Todo Web Application API",
    description="API for the Todo Web Application with user authentication and todo management",
    version="1.0.0"
)

# Get allowed origins from settings
cors_origins = settings.cors_allowed_origins

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
def startup_event():
    # Test database connectivity
    if not test_db_connection():
        print("Warning: Unable to connect to the database. Please check your DATABASE_URL configuration.")
        # Don't exit the application, just log the error
    else:
        print("Database connectivity test passed.")

    # Only create tables if not using PostgreSQL in production
    # In production, migrations should handle table creation
    if settings.environment != "production":
        from app.database.models import Base
        Base.metadata.create_all(bind=engine)
        print("Database tables created.")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/todos", tags=["Todos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Web Application API"}

@app.get("/health")
def health_check():
    # Test database connectivity as part of health check
    try:
        db_connected = test_db_connection()
        return {
            "status": "healthy" if db_connected else "degraded",
            "service": "Todo API",
            "database_connected": db_connected,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Todo API",
            "database_connected": False,
            "error": str(e),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }