# create_admin.py
from sqlalchemy.orm import Session
from auth import get_password_hash
from models import User
from database import SessionLocal

db: Session = SessionLocal()

admin_user = User(
    username="admin",
    hashed_password=get_password_hash("admin123"),  # choose a strong password
    role="admin"
)

db.add(admin_user)
db.commit()
db.close()

print("Admin user created successfully!")
