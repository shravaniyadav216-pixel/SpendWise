import os
from datetime import date

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="SpendWise",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend-url.replit.app")

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff 0%, #f8fbff 50%, #fff1f8 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Header */
.main-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    color: #2563eb;
    margin-bottom: 0.25rem;
}

.sub-title {
    text-align: center;
    color: #475569;
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
}

/* Card */
.glass-card {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
    border-radius: 22px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

.tag-pill {
    display: inline-block;
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    background: linear-gradient(90deg, #fde68a, #fca5a5);
    color: #4b2e05;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #1e3a8a;
    margin-bottom: 0.8rem;
}

/* Metric cards */
.metric-box {
    border-radius: 20px;
    padding: 1rem 1.1rem;
    color: white;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.10);
    margin-bottom: 0.7rem;
}

.metric-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); }
.metric-blue   { background: linear-gradient(135deg, #2563eb, #38bdf8); }
.metric-pink   { background: linear-gradient(135deg, #ec4899, #fb7185); }
.metric-green  { background: linear-gradient(135deg, #059669, #34d399); }

.metric-label {
    font-size: 0.95rem;
    font-weight: 600;
    opacity: 0.95;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    margin-top: 0.2rem;
}

/* Insights */
.insight-box {
    background: linear-gradient(135deg, #eef4ff, #f8eeff);
    border-left: 5px solid #6366f1;
    color: #334155;
    padding: 0.9rem 1rem;
    border-radius: 14px;
    margin-bottom: 0.75rem;
    font-weight: 500;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #312e81 100%);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    font-weight: 700;
    color: white;
    background: linear-gradient(90deg, #6d28d9, #2563eb);
}

.stButton > button:hover {
    opacity: 0.95;
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
}

/* IMPORTANT: radio text visible */
div[role="radiogroup"] label {
    color: #0f172a !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    font-size: 1rem !important;
}

div[role="radiogroup"] {
    gap: 1rem;
    margin-bottom: 0.8rem;
}

/* Make field labels dark and visible */
label, .stMarkdown, p, span, div {
    color: inherit;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Session State
# ---------------------------------------------------
defaults = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_email": "",
    "is_admin": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------
# Helper UI Functions
# ---------------------------------------------------
def show_header():
    st.markdown('<div class="main-title">💸 SpendWise</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Track expenses smartly, visualize your spending beautifully, and manage users with a powerful admin dashboard.</div>',
        unsafe_allow_html=True
    )


def metric_card(label: str, value: str, css_class: str):
    st.markdown(
        f"""
        <div class="metric-box {css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=20, **kwargs)
        return response
    except requests.exceptions.RequestException:
        return None


# ---------------------------------------------------
# Backend API Functions
# ---------------------------------------------------
def signup_user(name, email, password):
    return safe_request(
        "POST",
        f"{BACKEND_URL}/signup",
        json={"name": name, "email": email, "password": password}
    )


def login_user(email, password):
    return safe_request(
        "POST",
        f"{BACKEND_URL}/login",
        json={"email": email, "password": password}
    )


def logout_user(user_id):
    return safe_request("POST", f"{BACKEND_URL}/logout/{user_id}")


def get_dashboard(user_id):
    return safe_request("GET", f"{BACKEND_URL}/dashboard/{user_id}")


def add_expense_api(user_id, title, amount, category, expense_date, description):
    return safe_request(
        "POST",
        f"{BACKEND_URL}/expenses",
        json={
            "user_id": user_id,
            "title": title,
            "amount": amount,
            "category": category,
            "date": str(expense_date),
            "description": description
        }
    )


def get_expenses(user_id):
    return safe_request("GET", f"{BACKEND_URL}/expenses/{user_id}")


def filter_expenses(user_id, category=None, start_date=None, end_date=None):
    params = {}
    if category and category != "All":
        params["category"] = category
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)

    return safe_request("GET", f"{BACKEND_URL}/expenses/filter/{user_id}", params=params)


def update_expense_api(expense_id, title, amount, category, expense_date, description):
    return safe_request(
        "PUT",
        f"{BACKEND_URL}/expenses/{expense_id}",
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "date": str(expense_date),
            "description": description
        }
    )


def delete_expense_api(expense_id):
    return safe_request("DELETE", f"{BACKEND_URL}/expenses/{expense_id}")


def get_login_activity(user_id):
    return safe_request("GET", f"{BACKEND_URL}/login-activity/{user_id}")


def get_admin_dashboard(admin_email):
    return safe_request("GET", f"{BACKEND_URL}/admin/dashboard", params={"admin_email": admin_email})


def toggle_user_status(user_id, admin_email):
    return safe_request("PUT", f"{BACKEND_URL}/admin/users/{user_id}/toggle-active", params={"admin_email": admin_email})


# ---------------------------------------------------
# Auth Screen
# ---------------------------------------------------
def auth_screen():
    show_header()

    left, center, right = st.columns([1, 1.15, 1])

    with center:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="tag-pill">✨ Smart • Simple • Colorful • Full Stack</div>', unsafe_allow_html=True)

        st.markdown("#### Choose an option")
        auth_mode = st.radio(
            "Authentication",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if auth_mode == "Login":
            st.markdown('<div class="section-title">🔐 Welcome Back</div>', unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Login to SpendWise"):
                if not email.strip() or not password.strip():
                    st.warning("Please enter both email and password.")
                else:
                    response = login_user(email, password)

                    if response is None:
                        st.error("Backend connection failed. Make sure FastAPI is running.")
                    elif response.status_code == 200:
                        data = response.json()
                        st.session_state.logged_in = True
                        st.session_state.user_id = data["user"]["id"]
                        st.session_state.user_name = data["user"]["name"]
                        st.session_state.user_email = data["user"]["email"]
                        st.session_state.is_admin = data["user"]["is_admin"]
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        try:
                            st.error(response.json().get("detail", "Login failed."))
                        except Exception:
                            st.error("Login failed.")

        else:
            st.markdown('<div class="section-title">📝 Create Your Account</div>', unsafe_allow_html=True)

            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email Address", placeholder="Enter your email")
            password = st.text_input("Create Password", type="password", placeholder="Create password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")

            if st.button("Create Account"):
                if not name.strip() or not email.strip() or not password.strip() or not confirm_password.strip():
                    st.warning("Please fill all fields.")
                elif password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    response = signup_user(name, email, password)

                    if response is None:
                        st.error("Backend connection failed. Make sure FastAPI is running.")
                    elif response.status_code == 200:
                        st.success("Account created successfully. Please login now.")
                    else:
                        try:
                            st.error(response.json().get("detail", "Signup failed."))
                        except Exception:
                            st.error("Signup failed.")

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# User Dashboard
# ---------------------------------------------------
def user_dashboard_page():
    show_header()
    st.markdown(f"### 👋 Welcome, {st.session_state.user_name}")

    response = get_dashboard(st.session_state.user_id)

    if response is None:
        st.error("Could not connect to backend.")
        return

    if response.status_code != 200:
        st.error("Failed to load dashboard.")
        return

    data = response.json()

    total_count = data.get("total_expenses_count", 0)
    total_amount = data.get("total_amount_spent", 0.0)
    category_summary = data.get("category_summary", [])
    recent_expenses = data.get("recent_expenses", [])
    insights = data.get("insights", [])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("📌 Total Entries", str(total_count), "metric-purple")
    with c2:
        metric_card("💰 Total Spent", f"₹ {total_amount:.2f}", "metric-blue")
    with c3:
        metric_card("🧾 Categories", str(len(category_summary)), "metric-pink")
    with c4:
        metric_card("⚡ Recent Records", str(len(recent_expenses)), "metric-green")

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Category-wise Spending</div>', unsafe_allow_html=True)

        if category_summary:
            df_cat = pd.DataFrame(category_summary)
            fig = px.pie(df_cat, names="category", values="total_amount", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧠 SpendWise Insights</div>', unsafe_allow_html=True)

        if insights:
            for insight in insights:
                st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
        else:
            st.info("No insights available yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🕒 Recent Expenses</div>', unsafe_allow_html=True)

    if recent_expenses:
        df_recent = pd.DataFrame(recent_expenses)
        if "created_at" in df_recent.columns:
            df_recent = df_recent.drop(columns=["created_at"])
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("No recent expenses found.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# Add Expense Page
# ---------------------------------------------------
def add_expense_page():
    show_header()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ Add New Expense</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        title = st.text_input("Expense Title")
        amount = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"]
        )

    with c2:
        expense_date = st.date_input("Expense Date", value=date.today())
        description = st.text_area("Description")

    if st.button("Save Expense"):
        if not title.strip():
            st.warning("Please enter expense title.")
        else:
            response = add_expense_api(
                st.session_state.user_id,
                title,
                amount,
                category,
                expense_date,
                description
            )

            if response is None:
                st.error("Could not connect to backend.")
            elif response.status_code == 200:
                st.success("Expense added successfully.")
            else:
                try:
                    st.error(response.json().get("detail", "Failed to add expense."))
                except Exception:
                    st.error("Failed to add expense.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# View Expenses Page
# ---------------------------------------------------
def view_expenses_page():
    show_header()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 Expense History</div>', unsafe_allow_html=True)

    categories = ["All", "Food", "Travel", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"]

    f1, f2, f3 = st.columns(3)
    with f1:
        category_filter = st.selectbox("Filter by Category", categories)
    with f2:
        start_date = st.date_input("Start Date", value=None)
    with f3:
        end_date = st.date_input("End Date", value=None)

    if st.button("Apply Filters"):
        response = filter_expenses(
            st.session_state.user_id,
            category=category_filter,
            start_date=start_date,
            end_date=end_date
        )
    else:
        response = get_expenses(st.session_state.user_id)

    if response is None:
        st.error("Could not connect to backend.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if response.status_code != 200:
        st.error("Failed to fetch expenses.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    expenses = response.json()

    if not expenses:
        st.info("No expenses found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(expenses)
    display_cols = [c for c in ["id", "title", "amount", "category", "date", "description"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)

    st.markdown("---")
    st.markdown("#### ✏️ Edit or Delete Expense")

    selected_expense_id = st.selectbox("Select Expense ID", df["id"].tolist())
    selected_row = df[df["id"] == selected_expense_id].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        new_title = st.text_input("Edit Title", value=selected_row["title"])
        new_amount = st.number_input("Edit Amount", min_value=1.0, value=float(selected_row["amount"]))
        category_list = ["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"]
        default_index = category_list.index(selected_row["category"]) if selected_row["category"] in category_list else 0
        new_category = st.selectbox("Edit Category", category_list, index=default_index)

    with c2:
        new_date = st.date_input("Edit Date", value=pd.to_datetime(selected_row["date"]).date())
        new_description = st.text_area(
            "Edit Description",
            value="" if pd.isna(selected_row["description"]) else selected_row["description"]
        )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Update Expense"):
            response = update_expense_api(
                selected_expense_id,
                new_title,
                new_amount,
                new_category,
                new_date,
                new_description
            )
            if response is None:
                st.error("Could not connect to backend.")
            elif response.status_code == 200:
                st.success("Expense updated successfully.")
                st.rerun()
            else:
                try:
                    st.error(response.json().get("detail", "Update failed."))
                except Exception:
                    st.error("Update failed.")

    with b2:
        if st.button("Delete Expense"):
            response = delete_expense_api(selected_expense_id)
            if response is None:
                st.error("Could not connect to backend.")
            elif response.status_code == 200:
                st.success("Expense deleted successfully.")
                st.rerun()
            else:
                try:
                    st.error(response.json().get("detail", "Delete failed."))
                except Exception:
                    st.error("Delete failed.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# Reports Page
# ---------------------------------------------------
def reports_page():
    show_header()

    response = get_expenses(st.session_state.user_id)

    if response is None:
        st.error("Could not connect to backend.")
        return

    if response.status_code != 200:
        st.error("Failed to fetch expense data.")
        return

    expenses = response.json()
    if not expenses:
        st.info("No expense data available for reports.")
        return

    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Monthly Spending Report</div>', unsafe_allow_html=True)

    monthly_summary = df.groupby("month", as_index=False)["amount"].sum()
    fig_bar = px.bar(monthly_summary, x="month", y="amount", title="Monthly Expense Trend")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🥧 Category Distribution</div>', unsafe_allow_html=True)

        cat_summary = df.groupby("category", as_index=False)["amount"].sum()
        fig_pie = px.pie(cat_summary, names="category", values="amount")
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Expense Summary</div>', unsafe_allow_html=True)

        summary_df = (
            df.groupby("category")
            .agg(Total_Amount=("amount", "sum"), Entries=("amount", "count"))
            .reset_index()
        )
        st.dataframe(summary_df, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# Login Activity Page
# ---------------------------------------------------
def login_activity_page():
    show_header()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧾 Your Login Activity</div>', unsafe_allow_html=True)

    response = get_login_activity(st.session_state.user_id)

    if response is None:
        st.error("Could not connect to backend.")
    elif response.status_code == 200:
        data = response.json()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No login activity found.")
    else:
        st.error("Failed to load login activity.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------
def admin_dashboard_page():
    show_header()
    st.markdown("### 🛡️ Admin Control Center")

    response = get_admin_dashboard(st.session_state.user_email)

    if response is None:
        st.error("Could not connect to backend.")
        return

    if response.status_code != 200:
        st.error("Failed to load admin dashboard.")
        return

    data = response.json()

    total_users = data.get("total_users", 0)
    total_admins = data.get("total_admins", 0)
    active_users = data.get("active_users", 0)
    total_expense_entries = data.get("total_expense_entries", 0)
    total_system_expense_amount = data.get("total_system_expense_amount", 0.0)
    total_login_records = data.get("total_login_records", 0)
    recent_logins = data.get("recent_logins", [])
    users = data.get("users", [])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("👥 Total Users", str(total_users), "metric-purple")
    with c2:
        metric_card("💰 Total System Spend", f"₹ {total_system_expense_amount:.2f}", "metric-blue")
    with c3:
        metric_card("🧾 Total Expense Entries", str(total_expense_entries), "metric-pink")
    with c4:
        metric_card("🔐 Login Records", str(total_login_records), "metric-green")

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👥 User Overview</div>', unsafe_allow_html=True)

        overview_df = pd.DataFrame({
            "Type": ["Active Users", "Admins", "Other Users"],
            "Count": [active_users, total_admins, max(total_users - total_admins, 0)]
        })
        fig = px.bar(overview_df, x="Type", y="Count")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ System Usage</div>', unsafe_allow_html=True)

        usage_df = pd.DataFrame({
            "Metric": ["Expense Entries", "Login Records"],
            "Value": [total_expense_entries, total_login_records]
        })
        fig = px.pie(usage_df, names="Metric", values="Value")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧑‍💼 Registered Users</div>', unsafe_allow_html=True)

    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, use_container_width=True)

        non_admin_users = [u for u in users if u.get("email") != st.session_state.user_email]
        if non_admin_users:
            user_map = {f"{u['name']} ({u['email']})": u["user_id"] for u in non_admin_users}
            selected_user = st.selectbox("Select User", list(user_map.keys()))
            if st.button("Toggle User Active Status"):
                toggle_response = toggle_user_status(user_map[selected_user], st.session_state.user_email)
                if toggle_response is None:
                    st.error("Could not connect to backend.")
                elif toggle_response.status_code == 200:
                    st.success(toggle_response.json().get("message", "Updated successfully."))
                    st.rerun()
                else:
                    try:
                        st.error(toggle_response.json().get("detail", "Update failed."))
                    except Exception:
                        st.error("Update failed.")
    else:
        st.info("No users found.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🕒 Recent Login Activity</div>', unsafe_allow_html=True)

    if recent_logins:
        st.dataframe(pd.DataFrame(recent_logins), use_container_width=True)
    else:
        st.info("No recent login records found.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# Logout
# ---------------------------------------------------
def do_logout():
    if st.session_state.user_id is not None:
        logout_user(st.session_state.user_id)

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.is_admin = False
    st.success("Logged out successfully.")
    st.rerun()


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
def sidebar_navigation():
    st.sidebar.markdown("## 💼 SpendWise Panel")
    st.sidebar.markdown(f"**User:** {st.session_state.user_name}")
    st.sidebar.markdown(f"**Email:** {st.session_state.user_email}")

    if st.session_state.is_admin:
        return st.sidebar.radio(
            "Navigate",
            ["Admin Dashboard", "User Dashboard", "Add Expense", "View Expenses", "Reports", "Login Activity", "Logout"]
        )

    return st.sidebar.radio(
        "Navigate",
        ["User Dashboard", "Add Expense", "View Expenses", "Reports", "Login Activity", "Logout"]
    )


# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():
    if not st.session_state.logged_in:
        auth_screen()
    else:
        menu = sidebar_navigation()

        if menu == "User Dashboard":
            user_dashboard_page()
        elif menu == "Add Expense":
            add_expense_page()
        elif menu == "View Expenses":
            view_expenses_page()
        elif menu == "Reports":
            reports_page()
        elif menu == "Login Activity":
            login_activity_page()
        elif menu == "Admin Dashboard":
            admin_dashboard_page()
        elif menu == "Logout":
            do_logout()


if __name__ == "__main__":
    main()
