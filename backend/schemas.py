from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List


# -------------------------
# User Schemas
# -------------------------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Expense Schemas
# -------------------------
class ExpenseCreate(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=150)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=100)
    date: date
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    date: Optional[date] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Login Activity Schemas
# -------------------------
class LoginActivityResponse(BaseModel):
    id: int
    user_id: int
    login_time: datetime
    logout_time: Optional[datetime]
    status: str

    class Config:
        from_attributes = True


# -------------------------
# Admin / Dashboard Schemas
# -------------------------
class AdminUserStats(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    total_expenses: int
    total_amount_spent: float
    total_logins: int
    last_login: Optional[datetime]


class AdminDashboardStats(BaseModel):
    total_users: int
    total_admins: int
    active_users: int
    total_expense_entries: int
    total_system_expense_amount: float
    total_login_records: int
    recent_logins: List[LoginActivityResponse]
    users: List[AdminUserStats]


class MessageResponse(BaseModel):
    message: str