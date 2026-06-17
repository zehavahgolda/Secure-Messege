"""
seed.py — Populate the database with test data.

Usage:
  python seed.py

This script creates 3 test users and exchanges messages between them.
Safe to run multiple times — checks for existing users before creating.
"""

from server.models import create_tables, SessionLocal, User, Message
from server.auth import hash_password
from server.crypto import encrypt


def seed_database() -> None:
    """Create test users and messages."""
    
    # Create tables if they don't exist
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Create test users if they don't already exist
        users_to_create = [
            ("alice", "alice123"),
            ("bob", "bob456"),
            ("charlie", "charlie789"),
        ]
        
        created_users = {}
        for username, password in users_to_create:
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"User '{username}' already exists")
                created_users[username] = existing_user
            else:
                password_hash = hash_password(password)
                new_user = User(username=username, password_hash=password_hash)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                print(f"Created user: {username}")
                created_users[username] = new_user
        
        # Create some sample messages if none exist
        message_count = db.query(Message).count()
        if message_count == 0:
            messages = [
                ("alice", "bob", "Hey Bob, how are you?"),
                ("bob", "alice", "Hi Alice! I'm doing great!"),
                ("bob", "charlie", "Charlie, can you review my code?"),
                ("charlie", "bob", "Sure thing! Send it over."),
                ("alice", "charlie", "Welcome to the chat!"),
            ]
            
            for sender, recipient, content in messages:
                ciphertext = encrypt(content)
                message = Message(
                    sender=sender,
                    recipient=recipient,
                    ciphertext=ciphertext,
                )
                db.add(message)
                print(f"Created message: {sender} → {recipient}")
            
            db.commit()
        else:
            print(f"Database already has {message_count} messages")
        
        print("\nDatabase seeded successfully!")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
