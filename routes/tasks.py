from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
# Assuming these models and db object are available from app.models
from app.models import db, Book, Member, Fine, History
from sqlalchemy import func
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime 

task_bp = Blueprint("tasks", __name__) 

# ---------------- Dashboard (Endpoint: tasks.dashboard) ----------------
@task_bp.route("/dashboard")
@login_required
def dashboard():
    """Renders the main dashboard page."""
    try:
        # Fetch key metrics for the dashboard
        total_books = Book.query.count()
        total_members = Member.query.count()
        
        # Calculate total unpaid fines
        total_fines_unpaid = db.session.query(func.sum(Fine.amount)).filter(Fine.paid == False).scalar() or 0
        
        # Determine number of books currently checked out (not available)
        books_checked_out = Book.query.filter_by(available=False).count()
        
    except Exception as e:
        # Log error but use safe defaults if database queries fail
        print(f"Database error during dashboard load: {e}")
        total_books, total_members, total_fines_unpaid, books_checked_out = 0, 0, 0.0, 0

    return render_template(
        "dashboard.html", 
        total_books=total_books, 
        total_members=total_members,
        total_fines_unpaid=f'{total_fines_unpaid:.2f}',
        books_checked_out=books_checked_out
    )

# ---------------- Book Management (Endpoint: tasks.books_page) ----------------
@task_bp.route("/books")
@login_required
def books_page():
    """Renders the books management page (endpoint: tasks.books_page)."""
    books = Book.query.all()
    return render_template("books.html", books=books)

# ---------------- Member Management (Endpoint: tasks.members_page) ----------------
@task_bp.route("/members")
@login_required
def members_page():
    """Renders the members management page (endpoint: tasks.members_page)."""
    members = Member.query.all()
    return render_template("members.html", members=members)

# ---------------- Fine Payment (Endpoint: tasks.fine_payment_page) ----------------
@task_bp.route("/fine-payment")
@login_required
def fine_payment_page():
    """Renders the fine payment page (endpoint: tasks.fine_payment_page)."""
    fines = Fine.query.filter_by(paid=False).all()
    return render_template("fine-payment.html", fines=fines)

# ---------------- History (Endpoint: tasks.history_page) ----------------
@task_bp.route("/history")
@login_required
def history_page():
    """Renders the history/transaction log page (endpoint: tasks.history_page)."""
    records = History.query.order_by(History.timestamp.desc()).all()
    return render_template("history.html", records=records)

# ---------------- Reports (Endpoint: tasks.reports_page) ----------------
@task_bp.route("/reports")
@login_required
def reports_page():
    """Renders the reports page (endpoint: tasks.reports_page)."""
    # Placeholder report logic
    return render_template("reports.html") 

@task_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    """Renders and handles the settings configuration page."""
    # Placeholder for configuration settings (In a real app, these would come from a database table)
    settings_data = {
        'fine_rate': 5.00,  # Example: Fine rate per day
        'max_borrow_days': 14, # Example: Maximum days a book can be borrowed
        'app_version': '1.0.2'
    }

    if request.method == "POST":
        # Process settings updates here
        new_fine_rate = request.form.get('fine_rate')
        new_max_days = request.form.get('max_borrow_days')
        
      
        # Update the dictionary for display on successful update (in placeholder mode)
        settings_data['fine_rate'] = float(new_fine_rate) if new_fine_rate else settings_data['fine_rate']
        settings_data['max_borrow_days'] = int(new_max_days) if new_max_days else settings_data['max_borrow_days']
        
        flash("System settings updated successfully!", "success")
        return redirect(url_for('tasks.settings_page'))
        
    return render_template("settings.html", settings=settings_data)