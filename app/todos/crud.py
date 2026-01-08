from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database.models import Todo, User
from app.utils.security import get_current_user
from app.utils.schemas import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter()


@router.post("/", response_model=TodoResponse)
def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new todo for the authenticated user."""
    # Create the new todo
    db_todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        completed=todo_data.completed,
        user_id=current_user.id
    )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo


@router.get("/", response_model=List[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all todos for the authenticated user."""
    todos = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.id).all()
    return todos


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific todo for the authenticated user."""
    # Get the todo
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    # Check if todo exists and belongs to the current user
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this todo"
        )

    # Update the todo with provided values
    if todo_data.title is not None:
        db_todo.title = todo_data.title
    if todo_data.description is not None:
        db_todo.description = todo_data.description
    if todo_data.completed is not None:
        db_todo.completed = todo_data.completed

    db.commit()
    db.refresh(db_todo)

    return db_todo



@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific todo for the authenticated user."""
    # Get the todo
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    # Check if todo exists and belongs to the current user
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this todo"
        )

    # Delete the todo
    db.delete(db_todo)
    db.commit()

    return {"message": "Todo deleted successfully"}


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo_completion(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle the completion status of a specific todo for the authenticated user."""
    # Get the todo
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    # Check if todo exists and belongs to the current user
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this todo"
        )

    # Toggle the completion status
    db_todo.completed = not db_todo.completed

    db.commit()
    db.refresh(db_todo)

    return db_todo