import argparse
import sys
from database import SessionLocal
from models import Admin
from auth_utils import get_password_hash

def main():
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("email", type=str, help="Admin email address")
    parser.add_argument("password", type=str, help="Admin password")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == args.email).first()
        if existing:
            print(f"Admin with email {args.email} already exists.")
            sys.exit(1)
            
        admin = Admin(
            email=args.email,
            hashed_password=get_password_hash(args.password)
        )
        db.add(admin)
        db.commit()
        print(f"Admin {args.email} created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
