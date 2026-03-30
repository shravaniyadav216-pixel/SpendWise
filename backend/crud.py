from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import models
import schemas
from auth import hash_password, verify_password


# -------------------------
# User CRUD
# -------------------------
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        is_admin=is_admin,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    if not user.is_active:
        return None
    return user


# -------------------------
# Login Activity CRUD
# -------------------------
def create_login_activity(db: Session, user_id: int):
    activity = models.LoginActivity(
        user_id=user_id,
        login_time=datetime.utcnow(),
        status="logged_in"
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def logout_activity(db: Session, user_id: int):
    latest_activity = (
        db.query(models.LoginActivity)
        .filter(
            models.LoginActivity.user_id == user_id,
            models.LoginActivity.logout_time.is_(None)
        )
        .order_by(models.LoginActivity.login_time.desc())
        .first()
    )

    if latest_activity:
        latest_activity.logout_time = datetime.utcnow()
        latest_activity.status = "logged_out"
        db.commit()
        db.refresh(latest_activity)

    return latest_activity


def get_user_login_activities(db: Session, user_id: int):
    return (
        db.query(models.LoginActivity)
        .filter(models.LoginActivity.user_id == user_id)
        .order_by(models.LoginActivity.login_time.desc())
        .all()
    )


# -------------------------
# Expense CRUD
# -------------------------
def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(
        user_id=expense.user_id,
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        description=expense.description
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses_by_user(db: Session, user_id: int):
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .order_by(models.Expense.date.desc(), models.Expense.created_at.desc())
        .all()
    )


def get_expense_by_id(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()


def update_expense(db: Session, expense_id: int, expense_data: schemas.ExpenseUpdate):
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None

    update_data = expense_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int):
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None

    db.delete(db_expense)
    db.commit()
    return db_expense


def get_filtered_expenses(db: Session, user_id: int, category: str = None, start_date=None, end_date=None):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)

    if category:
        query = query.filter(models.Expense.category == category)

    if start_date:
        query = query.filter(models.Expense.date >= start_date)

    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    return query.order_by(models.Expense.date.desc(), models.Expense.created_at.desc()).all()


# -------------------------
# User Dashboard Helpers
# -------------------------
def get_total_expense_amount_by_user(db: Session, user_id: int) -> float:
    total = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0.0))
        .filter(models.Expense.user_id == user_id)
        .scalar()
    )
    return float(total or 0.0)


def get_total_expense_count_by_user(db: Session, user_id: int) -> int:
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .count()
    )


def get_category_summary_by_user(db: Session, user_id: int):
    results = (
        db.query(
            models.Expense.category,
            func.sum(models.Expense.amount).label("total_amount"),
            func.count(models.Expense.id).label("count")
        )
        .filter(models.Expense.user_id == user_id)
        .group_by(models.Expense.category)
        .all()
    )

    return [
        {
            "category": row.category,
            "total_amount": float(row.total_amount or 0.0),
            "count": row.count
        }
        for row in results
    ]


# -------------------------
# Admin Dashboard Helpers
# -------------------------
def get_admin_dashboard_stats(db: Session):
    total_users = db.query(models.User).count()
    total_admins = db.query(models.User).filter(models.User.is_admin == True).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    total_expense_entries = db.query(models.Expense).count()
    total_system_expense_amount = db.query(func.coalesce(func.sum(models.Expense.amount), 0.0)).scalar() or 0.0
    total_login_records = db.query(models.LoginActivity).count()

    recent_logins = (
        db.query(models.LoginActivity)
        .order_by(models.LoginActivity.login_time.desc())
        .limit(10)
        .all()
    )

    all_users = db.query(models.User).order_by(models.User.created_at.desc()).all()

    user_stats_list = []
    for user in all_users:
        total_expenses = (
            db.query(models.Expense)
            .filter(models.Expense.user_id == user.id)
            .count()
        )

        total_amount_spent = (
            db.query(func.coalesce(func.sum(models.Expense.amount), 0.0))
            .filter(models.Expense.user_id == user.id)
            .scalar()
            or 0.0
        )

        total_logins = (
            db.query(models.LoginActivity)
            .filter(models.LoginActivity.user_id == user.id)
            .count()
        )

        last_login = (
            db.query(models.LoginActivity.login_time)
            .filter(models.LoginActivity.user_id == user.id)
            .order_by(models.LoginActivity.login_time.desc())
            .first()
        )

        user_stats_list.append({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "total_expenses": total_expenses,
            "total_amount_spent": float(total_amount_spent),
            "total_logins": total_logins,
            "last_login": last_login[0] if last_login else None
        })

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "active_users": active_users,
        "total_expense_entries": total_expense_entries,
        "total_system_expense_amount": float(total_system_expense_amount),
        "total_login_records": total_login_records,
        "recent_logins": recent_logins,
        "users": user_stats_list
    }