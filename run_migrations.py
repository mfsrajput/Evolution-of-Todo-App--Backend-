#!/usr/bin/env python
"""
Migration runner script for production environments like Render.
This script allows manual execution of Alembic migrations.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    """Run alembic migrations to upgrade to the latest version."""
    try:
        # Run alembic upgrade to head
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], check=True, capture_output=True, text=True)

        print("Migrations completed successfully!")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: Alembic is not installed or not in PATH")
        print("Please make sure to install alembic: pip install alembic")
        return False

def check_migrations_status():
    """Check the current migration status."""
    try:
        result = subprocess.run([
            "alembic", "current"
        ], check=True, capture_output=True, text=True)

        print("Current migration status:")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error checking migration status: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: Alembic is not installed or not in PATH")
        return False

def generate_migration(message):
    """Generate a new migration file."""
    try:
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", "-m", message
        ], check=True, capture_output=True, text=True)

        print(f"Migration generated: {result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error generating migration: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: Alembic is not installed or not in PATH")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_migrations.py upgrade    # Run migrations to latest version")
        print("  python run_migrations.py current    # Check current migration status")
        print("  python run_migrations.py generate \"message\"    # Generate new migration")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Validate DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set")
        sys.exit(1)

    print(f"Using database: {'PostgreSQL' if 'postgresql' in database_url.lower() else 'SQLite'}")

    if command == "upgrade":
        success = run_migrations()
        sys.exit(0 if success else 1)
    elif command == "current":
        success = check_migrations_status()
        sys.exit(0 if success else 1)
    elif command == "generate":
        if len(sys.argv) < 3:
            print("Error: Please provide a message for the migration")
            print("Usage: python run_migrations.py generate \"migration message\"")
            sys.exit(1)
        message = sys.argv[2]
        success = generate_migration(message)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: upgrade, current, generate")
        sys.exit(1)

if __name__ == "__main__":
    main()