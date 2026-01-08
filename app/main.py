from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Validate required environment variables at startup
required_env_vars = [
    "DATABASE_URL",
    "SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES"
]

for var in required_env_vars:
    if not os.getenv(var):
        print(f"Error: Required environment variable {var} is not set")
        sys.exit(1)

# Import routers
from app.auth.auth import router as auth_router
from app.todos.crud import router as todos_router
from app.database.database import engine, test_db_connection

app = FastAPI(
    title="Todo Web Application API",
    description="API for the Todo Web Application with user authentication and todo management",
    version="1.0.0"
)

# Get allowed origins from environment variable
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
# Remove any empty strings and strip whitespace
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

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
        print("Error: Unable to connect to the database. Please check your DATABASE_URL configuration.")
        sys.exit(1)

    print("Database connectivity test passed.")

    # Only create tables if not using PostgreSQL in production
    # In production, migrations should handle table creation
    import os
    if os.getenv("ENVIRONMENT") != "production":
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
    db_connected = test_db_connection()
    return {
        "status": "healthy",
        "service": "Todo API",
        "database_connected": db_connected
    }