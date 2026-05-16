"""
client.py — CLI terminal client for Secure Messenger.

A command-line interface where users can:
1. Register or login
2. View message history
3. Type messages to send
4. Receive incoming messages in real-time via SSE stream

Usage:
  python -m client.client

Example:
  $ python -m client.client
  === Secure Messenger ===
  1) Register
  2) Login
  Choose (1/2): 2
  Username: alice
  Password: ••••••••
  
  Welcome, alice!
  (type messages and press Enter, or type 'quit' to exit)
  
  > hello bob
  [alice → bob]: hello bob
  
  [bob → alice]: hi alice!
"""

import json
import threading
import requests
from getpass import getpass
from urllib.parse import urljoin


BASE_URL = "http://127.0.0.1:8000"


class MessengerClient:
    """CLI client for Secure Messenger."""
    
    def __init__(self):
        self.username = None
        self.token = None
        self.session = requests.Session()
    
    def register(self):
        """Register a new user."""
        print("\n=== Register ===")
        username = input("Username: ").strip()
        password = getpass("Password: ")
        
        response = self.session.post(
            urljoin(BASE_URL, "/register"),
            json={"username": username, "password": password}
        )
        
        if response.status_code == 201:
            print(f"✅ Registered as {username}!")
            return True
        else:
            print(f"❌ Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    
    def login(self):
        """Login with username and password."""
        print("\n=== Login ===")
        username = input("Username: ").strip()
        password = getpass("Password: ")
        
        response = self.session.post(
            urljoin(BASE_URL, "/login"),
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.username = username
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print(f"✅ Logged in as {username}!")
            return True
        else:
            print(f"❌ Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    
    def get_message_history(self):
        """Fetch and display all messages for this user."""
        response = self.session.get(urljoin(BASE_URL, "/messages"))
        
        if response.status_code == 200:
            messages = response.json()
            if messages:
                print("\n=== Message History ===")
                for msg in messages:
                    sender = msg["sender"]
                    content = msg["content"]
                    print(f"  [{sender}]: {content}")
            else:
                print("\n(No messages yet)")
        else:
            print(f"❌ Failed to fetch messages")
    
    def send_message(self, recipient, content):
        """Send a message to a recipient."""
        response = self.session.post(
            urljoin(BASE_URL, "/messages"),
            json={"content": content, "recipient": recipient}
        )
        
        if response.status_code == 201:
            print(f"✅ Sent to {recipient}")
        else:
            print(f"❌ Failed to send: {response.json().get('detail', 'Unknown error')}")
    
    def listen_to_stream(self):
        """
        Background thread that listens to SSE stream.
        Prints incoming messages as they arrive.
        """
        try:
            response = self.session.get(
                urljoin(BASE_URL, "/stream"),
                stream=True,
                timeout=None
            )
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                # Parse SSE format: "data: {json}"
                line_str = line.decode() if isinstance(line, bytes) else line
                if line_str.startswith("data: "):
                    try:
                        message = json.loads(line_str[6:])
                        sender = message.get("sender", "Unknown")
                        content = message.get("content", "")
                        print(f"\n  [{sender}]: {content}")
                        print(f"  > ", end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        
        except Exception as e:
            print(f"❌ Stream error: {e}")
    
    def run(self):
        """Main CLI loop."""
        print("=== Secure Messenger ===")
        
        # Auth
        while not self.token:
            choice = input("\n1) Register\n2) Login\nChoose (1/2): ").strip()
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            else:
                print("Invalid choice")
        
        # Show history
        self.get_message_history()
        
        # Start background listener thread
        listener_thread = threading.Thread(target=self.listen_to_stream, daemon=True)
        listener_thread.start()
        
        # Main input loop
        print(f"\nWelcome, {self.username}!")
        print("(type 'send <recipient> <message>' to send, or 'quit' to exit)\n")
        
        while True:
            try:
                user_input = input("  > ").strip()
                
                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break
                
                if user_input.lower().startswith("send "):
                    parts = user_input[5:].split(" ", 1)
                    if len(parts) == 2:
                        recipient, message = parts
                        self.send_message(recipient, message)
                    else:
                        print("Usage: send <recipient> <message>")
                
                elif user_input.lower() == "history":
                    self.get_message_history()
                
                else:
                    print("Unknown command. Try: send <recipient> <message>, history, or quit")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    client = MessengerClient()
    client.run()
