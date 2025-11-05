#!/usr/bin/env python3
"""
Script to add sample Indian data to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random

# Sample Indian names
indian_members = [
    {"name": "Rahul Sharma", "email": "rahul.sharma@email.com", "phone": "9876543210"},
    {"name": "Priya Patel", "email": "priya.patel@email.com", "phone": "9876543211"},
    {"name": "Amit Kumar", "email": "amit.kumar@email.com", "phone": "9876543212"},
    {"name": "Sneha Reddy", "email": "sneha.reddy@email.com", "phone": "9876543213"},
    {"name": "Vikram Singh", "email": "vikram.singh@email.com", "phone": "9876543214"},
    {"name": "Anjali Gupta", "email": "anjali.gupta@email.com", "phone": "9876543215"},
    {"name": "Rohit Verma", "email": "rohit.verma@email.com", "phone": "9876543216"},
    {"name": "Kavita Joshi", "email": "kavita.joshi@email.com", "phone": "9876543217"},
    {"name": "Arjun Malhotra", "email": "arjun.malhotra@email.com", "phone": "9876543218"},
    {"name": "Divya Nair", "email": "divya.nair@email.com", "phone": "9876543219"},
    {"name": "Karan Mehta", "email": "karan.mehta@email.com", "phone": "9876543220"},
    {"name": "Pooja Iyer", "email": "pooja.iyer@email.com", "phone": "9876543221"},
    {"name": "Manoj Desai", "email": "manoj.desai@email.com", "phone": "9876543222"},
    {"name": "Swati Chatterjee", "email": "swati.chatterjee@email.com", "phone": "9876543223"},
    {"name": "Deepak Shah", "email": "deepak.shah@email.com", "phone": "9876543224"}
]

indian_books = [
    {"title": "The God of Small Things", "author": "Arundhati Roy", "isbn": "9788184000665"},
    {"title": "Wings of Fire", "author": "A.P.J. Abdul Kalam", "isbn": "9788173714513"},
    {"title": "India After Gandhi", "author": "Ramachandra Guha", "isbn": "9780670082968"},
    {"title": "The White Tiger", "author": "Aravind Adiga", "isbn": "9788184003192"},
    {"title": "Midnight's Children", "author": "Salman Rushdie", "isbn": "9780224064409"},
    {"title": "The Argumentative Indian", "author": "Amartya Sen", "isbn": "9780143065167"},
    {"title": "Train to Pakistan", "author": "Khushwant Singh", "isbn": "9780143066485"},
    {"title": "The Discovery of India", "author": "Jawaharlal Nehru", "isbn": "9780195623597"},
    {"title": "Mahatma Gandhi: The Man Who Became One", "author": "Thomas Weber", "isbn": "9788129135814"},
    {"title": "Malgudi Days", "author": "R.K. Narayan", "isbn": "9780143030080"},
    {"title": "The Great Indian Novel", "author": "Shashi Tharoor", "isbn": "9780140127222"},
    {"title": "India Unbound", "author": "Gurcharan Das", "isbn": "9780670083613"},
    {"title": "The Inheritance of Loss", "author": "Kiran Desai", "isbn": "9780802144111"},
    {"title": "A Fine Balance", "author": "Rohinton Mistry", "isbn": "9781400030656"},
    {"title": "The Namesake", "author": "Jhumpa Lahiri", "isbn": "9780618485222"},
    {"title": "The Sacred and Profane", "author": "Anita Nair", "isbn": "9780143029742"},
    {"title": "The Hungry Tide", "author": "Amitav Ghosh", "isbn": "9780143064770"},
    {"title": "The Palace of Illusions", "author": "Chitra Banerjee Divakaruni", "isbn": "9780345458522"},
    {"title": "The Immortals of Meluha", "author": "Amish Tripathi", "isbn": "9789380658745"},
    {"title": "The Mahabharata", "author": "C. Rajagopalachari", "isbn": "9788172763655"},
    {"title": "The Ramayana", "author": "R.K. Narayan", "isbn": "9780143039695"},
    {"title": "Chanakya's Chant", "author": "Ashwin Sanghi", "isbn": "9789380349305"},
    {"title": "The Lost River", "author": "Michel Danino", "isbn": "9780143068648"},
    {"title": "The Ocean of Churn", "author": "Sanjeev Sanyal", "isbn": "9780670088014"},
    {"title": "India: A History", "author": "John Keay", "isbn": "9780802137975"}
]

def add_sample_data():
    """Add sample Indian data to the database"""
    try:
        # Import here to avoid import issues if app is not properly configured
        from app import create_app
        from app.models import db, Member, Book, Fine, History

        app = create_app()

        with app.app_context():
            # Clear existing data
            print("Clearing existing data...")
            History.query.delete()
            Fine.query.delete()
            Book.query.delete()
            Member.query.delete()
            db.session.commit()

            # Add members
            print("Adding Indian members...")
            members = []
            for member_data in indian_members:
                member = Member(
                    name=member_data["name"],
                    email=member_data["email"],
                    phone=member_data["phone"]
                )
                members.append(member)
                db.session.add(member)

            db.session.commit()
            print(f"Added {len(members)} members")

            # Add books
            print("Adding Indian books...")
            books = []
            for book_data in indian_books:
                book = Book(
                    title=book_data["title"],
                    author=book_data["author"],
                    isbn=book_data["isbn"],
                    available=random.choice([True, False])
                )
                books.append(book)
                db.session.add(book)

            db.session.commit()
            print(f"Added {len(books)} books")

            # Add fines (in rupees)
            print("Adding fines...")
            fine_amounts = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 750, 1000]
            fine_reasons = ["Late return", "Book damage", "Lost book", "Overdue charges", "Processing fee"]

            fines = []
            for i in range(20):
                member = random.choice(members)
                amount = random.choice(fine_amounts)
                reason = random.choice(fine_reasons)
                paid = random.choice([True, False])

                fine = Fine(
                    member_id=member.id,
                    amount=amount,
                    reason=reason,
                    paid=paid,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                fines.append(fine)
                db.session.add(fine)

            db.session.commit()
            print(f"Added {len(fines)} fines")

            # Add history
            print("Adding transaction history...")
            history_count = 50
            actions = ["borrow", "return"]

            for i in range(history_count):
                member = random.choice(members)
                book = random.choice(books)
                action = random.choice(actions)
                timestamp = datetime.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))

                history = History(
                    member_id=member.id,
                    book_id=book.id,
                    action=action,
                    timestamp=timestamp
                )
                db.session.add(history)

            db.session.commit()
            print(f"Added {history_count} history records")

            # Update some book availability based on history
            print("Updating book availability...")
            for history in History.query.filter_by(action="borrow").limit(10).all():
                if random.random() > 0.3:  # 70% chance book is still borrowed
                    history.book.available = False

            db.session.commit()

            print("\n✅ Sample Indian data added successfully!")
            print(f"📊 Summary:")
            print(f"   - Members: {len(members)}")
            print(f"   - Books: {len(books)}")
            print(f"   - Fines: {len(fines)}")
            print(f"   - History: {history_count}")

            return True

    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    success = add_sample_data()
    sys.exit(0 if success else 1)