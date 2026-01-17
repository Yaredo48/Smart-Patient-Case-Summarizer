"""
Create a test user in the database for the Smart Patient Case Summarizer
"""
import sys
sys.path.append('/home/yared/Documents/ML project/Smart-Patient-Case-Summarizer/backend')

from app.core.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "doctor@test.com").first()
        
        if existing_user:
            print("✅ Test user already exists!")
            print("\n📧 Email: doctor@test.com")
            print("🔑 Password: password123")
            return
        
        # Create test user
        test_user = User(
            email="doctor@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Test User",
            role="doctor",
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("\n" + "="*50)
        print("📋 TEST USER CREDENTIALS:")
        print("="*50)
        print("📧 Email: doctor@test.com")
        print("🔑 Password: password123")
        print("="*50)
        print("\nYou can now log in at: http://localhost:5173/login")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
