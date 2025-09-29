from sqlalchemy.orm import Session
from database import SessionLocal      
from models import User                
from auth import get_password_hash     

db: Session = SessionLocal()
old_admin = db.query(User).filter(User.username == "admin").first()
if old_admin:
    db.delete(old_admin)
    db.commit()

new_admin = User(
    username="admin",
    hashed_password=get_password_hash("admin1234"),
    role="admin"
)
db.add(new_admin)
db.commit()
db.close()

print("Admin reset successfully!")
