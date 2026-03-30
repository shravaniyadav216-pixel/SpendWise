from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

import models
import schemas
import crud
from database import engine, Base, get_db
from utils import generate_spending_insights

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SpendWise Backend API",
    description="Personal Expense Tracker with Admin Dashboard",
    version="1.0.0"
)


# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
def create_default_admin():
    from schemas import UserCreate
    from crud import get_user_by_email, create_user
    from database import SessionLocal

    db = SessionLocal()
    try:
        admin_email = "admin@spendwise.com"
        existing_admin = get_user_by_email(db, admin_email)

        if not existing_admin:
            admin_user = UserCreate(
                name="Admin",
                email=admin_email,
                password="admin123"
            )
            create_user(db, admin_user, is_admin=True)
            print("Default admin created: admin@spendwise.com / admin123")
    finally:
        db.close()


# -------------------------
# Root Route
# -------------------------
@app.get("/")
def home():
    return {"message": "Welcome to SpendWise Backend API"}


# -------------------------
# Authentication Routes
# -------------------------
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user(db, user)
    return new_user


@app.post("/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email, password, or inactive account")

    crud.create_login_activity(db, user.id)

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }


@app.post("/logout/{user_id}", response_model=schemas.MessageResponse)
def logout(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.logout_activity(db, user_id)
    return {"message": "Logout successful"}


# -------------------------
# User Routes
# -------------------------
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------
# Expense Routes
# -------------------------
@app.post("/expenses", response_model=schemas.ExpenseResponse)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, expense.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_expense = crud.create_expense(db, expense)
    return new_expense


@app.get("/expenses/{user_id}", response_model=List[schemas.ExpenseResponse])
def get_user_expenses(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_expenses_by_user(db, user_id)


@app.get("/expenses/filter/{user_id}", response_model=List[schemas.ExpenseResponse])
def filter_user_expenses(
    user_id: int,
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_filtered_expenses(db, user_id, category, start_date, end_date)


@app.put("/expenses/{expense_id}", response_model=schemas.ExpenseResponse)
def edit_expense(expense_id: int, expense_data: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    updated_expense = crud.update_expense(db, expense_id, expense_data)
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return updated_expense


@app.delete("/expenses/{expense_id}", response_model=schemas.MessageResponse)
def remove_expense(expense_id: int, db: Session = Depends(get_db)):
    deleted_expense = crud.delete_expense(db, expense_id)
    if not deleted_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return {"message": "Expense deleted successfully"}


# -------------------------
# User Dashboard Routes
# -------------------------
@app.get("/dashboard/{user_id}")
def user_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_amount = crud.get_total_expense_amount_by_user(db, user_id)
    total_count = crud.get_total_expense_count_by_user(db, user_id)
    category_summary = crud.get_category_summary_by_user(db, user_id)
    recent_expenses = crud.get_expenses_by_user(db, user_id)[:5]
    insights = generate_spending_insights(category_summary, total_amount)

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "total_expenses_count": total_count,
        "total_amount_spent": total_amount,
        "category_summary": category_summary,
        "recent_expenses": recent_expenses,
        "insights": insights
    }


@app.get("/login-activity/{user_id}", response_model=List[schemas.LoginActivityResponse])
def user_login_activity(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_user_login_activities(db, user_id)


# -------------------------
# Admin Routes
# -------------------------
@app.get("/admin/dashboard", response_model=schemas.AdminDashboardStats)
def admin_dashboard(admin_email: str, db: Session = Depends(get_db)):
    admin_user = crud.get_user_by_email(db, admin_email)

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")

    return crud.get_admin_dashboard_stats(db)


@app.get("/admin/users", response_model=List[schemas.UserResponse])
def admin_get_all_users(admin_email: str, db: Session = Depends(get_db)):
    admin_user = crud.get_user_by_email(db, admin_email)

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")

    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return users


@app.put("/admin/users/{user_id}/toggle-active", response_model=schemas.MessageResponse)
def toggle_user_active_status(user_id: int, admin_email: str, db: Session = Depends(get_db)):
    admin_user = crud.get_user_by_email(db, admin_email)

    if not admin_user or not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot deactivate admin user")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    status = "activated" if user.is_active else "deactivated"
    return {"message": f"User has been {status} successfully"}