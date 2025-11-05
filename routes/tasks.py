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
    try:
        # Calculate real metrics for reports
        total_books = Book.query.count()
        total_members = Member.query.count()
        available_books = Book.query.filter_by(available=True).count()
        borrowed_books = total_books - available_books

        # Calculate fines statistics
        total_fines = db.session.query(func.sum(Fine.amount)).scalar() or 0
        paid_fines = db.session.query(func.sum(Fine.amount)).filter(Fine.paid == True).scalar() or 0
        unpaid_fines = total_fines - paid_fines

        # Get recent history
        recent_history = History.query.order_by(History.timestamp.desc()).limit(10).all()

        # Calculate collection rate
        collection_rate = (paid_fines / total_fines * 100) if total_fines > 0 else 0

        return render_template("reports.html",
                             total_books=total_books,
                             total_members=total_members,
                             available_books=available_books,
                             borrowed_books=borrowed_books,
                             total_fines=f'{total_fines:.2f}',
                             paid_fines=f'{paid_fines:.2f}',
                             unpaid_fines=f'{unpaid_fines:.2f}',
                             collection_rate=f'{collection_rate:.1f}',
                             recent_history=recent_history)
    except Exception as e:
        print(f"Database error during reports load: {e}")
        return render_template("reports.html")

# ---------------- Export History PDF ----------------
@task_bp.route("/export/history")
@login_required
def export_history_pdf():
    """Generate and export history data as PDF."""
    try:
        # Get filter parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')

        # Query history data
        query = History.query.order_by(History.timestamp.desc())

        # Apply filters if provided
        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(History.timestamp >= date_from_dt)
            except ValueError:
                return "Invalid date_from format. Use YYYY-MM-DD", 400

        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(History.timestamp <= date_to_dt)
            except ValueError:
                return "Invalid date_to format. Use YYYY-MM-DD", 400

        if status:
            query = query.filter(History.action == status)

        records = query.all()

        if not records:
            return "No history records found for the specified criteria", 404

        # Create PDF
        response = make_response()
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=history_export.pdf'

        # Generate PDF in memory
        from io import BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Content
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        story.append(Paragraph("संकष्ट पुस्तकालय वित्त प्रबंधन प्रणाली - इतिहास रिपोर्ट", title_style))
        story.append(Spacer(1, 20))

        # Export info
        info_style = styles['Normal']
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"बनाया गया: {export_date}", info_style))
        story.append(Paragraph(f"कुल रिकॉर्ड: {len(records)}", info_style))
        story.append(Spacer(1, 20))

        # Table data
        table_data = [['ID', 'Member Name', 'Book Title', 'Action', 'Date & Time']]

        for record in records:
            table_data.append([
                str(record.id),
                record.member.name if record.member else 'Unknown',
                record.book.title if record.book else 'Unknown',
                record.action.title(),
                record.timestamp.strftime("%Y-%m-%d %H:%M")
            ])

        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2*inch, 2.5*inch, 1*inch, 1.5*inch])

        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        story.append(table)

        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        response.data = pdf_data
        return response

    except Exception as e:
        print(f"Error generating history PDF: {e}")
        return f"Unable to generate PDF: {str(e)}", 500

# ---------------- Export Reports PDF ----------------
@task_bp.route("/export/reports")
@login_required
def export_reports_pdf():
    """Generate and export reports data as PDF."""
    try:
        # Calculate metrics
        total_books = Book.query.count()
        total_members = Member.query.count()
        available_books = Book.query.filter_by(available=True).count()
        borrowed_books = total_books - available_books

        # Calculate fines statistics
        total_fines = db.session.query(func.sum(Fine.amount)).scalar() or 0
        paid_fines = db.session.query(func.sum(Fine.amount)).filter(Fine.paid == True).scalar() or 0
        unpaid_fines = total_fines - paid_fines
        collection_rate = (paid_fines / total_fines * 100) if total_fines > 0 else 0

        # Get recent history
        recent_history = History.query.order_by(History.timestamp.desc()).limit(20).all()

        # Get top defaulters
        defaulters = db.session.query(
            Member.name,
            func.sum(Fine.amount).label('total_fines')
        ).join(Fine).filter(Fine.paid == False).group_by(Member.id, Member.name).order_by(func.sum(Fine.amount).desc()).limit(10).all()

        # Create PDF
        response = make_response()
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reports_export.pdf'

        from io import BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        story.append(Paragraph("Library Management System - Analytics Report", title_style))
        story.append(Spacer(1, 20))

        # Export info
        info_style = styles['Normal']
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {export_date}", info_style))
        story.append(Spacer(1, 20))

        # Statistics Summary
        story.append(Paragraph("Library Statistics", styles['Heading2']))
        story.append(Spacer(1, 12))

        stats_data = [
            ['Metric', 'Value'],
            ['Total Books', str(total_books)],
            ['Available Books', str(available_books)],
            ['Borrowed Books', str(borrowed_books)],
            ['Total Members', str(total_members)],
            ['Total Fines', f'${total_fines:.2f}'],
            ['Paid Fines', f'${paid_fines:.2f}'],
            ['Unpaid Fines', f'${unpaid_fines:.2f}'],
            ['Collection Rate', f'{collection_rate:.1f}%']
        ]

        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Top Defaulters
        if defaulters:
            story.append(Paragraph("Top Defaulters (Unpaid Fines)", styles['Heading2']))
            story.append(Spacer(1, 12))

            defaulter_data = [['Member Name', 'Total Unpaid Fines']]
            for defaulter in defaulters:
                defaulter_data.append([defaulter.name, f'${defaulter.total_fines:.2f}'])

            defaulter_table = Table(defaulter_data, colWidths=[2.5*inch, 1.5*inch])
            defaulter_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))

            story.append(defaulter_table)
            story.append(Spacer(1, 20))

        # Recent Activity
        if recent_history:
            story.append(Paragraph("Recent Activity", styles['Heading2']))
            story.append(Spacer(1, 12))

            activity_data = [['ID', 'Member', 'Book', 'Action', 'Date']]
            for record in recent_history:
                activity_data.append([
                    str(record.id),
                    record.member.name[:15] + '...' if record.member and len(record.member.name) > 15 else (record.member.name if record.member else 'Unknown'),
                    record.book.title[:20] + '...' if record.book and len(record.book.title) > 20 else (record.book.title if record.book else 'Unknown'),
                    record.action.title(),
                    record.timestamp.strftime("%Y-%m-%d")
                ])

            activity_table = Table(activity_data, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1*inch, 1*inch])
            activity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            story.append(activity_table)

        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        response.data = pdf_data
        return response

    except Exception as e:
        print(f"Error generating reports PDF: {e}")
        return f"Unable to generate PDF: {str(e)}", 500

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