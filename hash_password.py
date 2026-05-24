#!/usr/bin/env python3
"""
Utility script to generate password hashes for operator accounts.
Run this script to generate a bcrypt hash for a password.
"""

from werkzeug.security import generate_password_hash
import getpass


def main():
    print("=== Password Hash Generator ===")
    print("Generate bcrypt hashes for operator passwords.\n")
    
    password = getpass.getpass("Enter password to hash: ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("Error: Passwords do not match.")
        return
    
    if not password:
        print("Error: Password cannot be empty.")
        return
    
    # Generate hash
    password_hash = generate_password_hash(password)
    
    print("\n=== Generated Hash ===")
    print(f"Password Hash: {password_hash}")
    print("\nUse this hash in the MySQL 'operators' table 'password_hash' field.")


if __name__ == "__main__":
    main()
