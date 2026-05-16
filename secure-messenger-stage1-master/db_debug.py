from server.models import SessionLocal, User
from server.auth import verify_password

session = SessionLocal()
for u in session.query(User).all():
    print(u.username, verify_password('bob456', u.password_hash), verify_password('alice123', u.password_hash))
