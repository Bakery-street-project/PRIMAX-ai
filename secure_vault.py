"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: secure_vault.py                                                       ║
║  Generated: 2025-12-26T10:00:41.711541                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     PRIMAX-AI SECURE VAULT SYSTEM                             ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-VAULT-BSP-2025                                             ║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import hashlib
import secrets
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import json
from datetime import datetime

WATERMARK = "PRIMAX-VAULT-BSP-2025"
VAULT_DIR = Path.home() / "claude_enterprise" / "workspace" / "PRIMAX-ai" / ".vault"
SALT_FILE = VAULT_DIR / ".salt"
AUTH_FILE = VAULT_DIR / ".auth"


class SecureVault:
    """Encrypted vault with hashed password authentication"""

    def __init__(self):
        self.vault_dir = VAULT_DIR
        self.vault_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,  # High iteration count for security
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _hash_password(self, password: str, salt: bytes) -> str:
        """Hash password with salt for authentication"""
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000).hex()

    def initialize(self, password: str):
        """Initialize vault with password"""
        # Generate salt
        salt = secrets.token_bytes(32)

        # Hash password for authentication
        password_hash = self._hash_password(password, salt)

        # Store salt and hash
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        os.chmod(SALT_FILE, 0o600)

        auth_data = {
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "watermark": WATERMARK,
            "owner": "Kiliaan Vanvoorden (@BoozeLee)",
            "copyright": "© 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED",
        }

        with open(AUTH_FILE, "w") as f:
            json.dump(auth_data, f, indent=2)
        os.chmod(AUTH_FILE, 0o600)

        print(f"✓ Vault initialized with watermark: {WATERMARK}")
        print(f"✓ Location: {self.vault_dir}")
        print(f"✓ Permissions: 700 (owner only)")

    def authenticate(self, password: str) -> bool:
        """Authenticate user with password"""
        if not SALT_FILE.exists() or not AUTH_FILE.exists():
            raise FileNotFoundError("Vault not initialized. Run 'initialize' first.")

        # Load salt and stored hash
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

        with open(AUTH_FILE, "r") as f:
            auth_data = json.load(f)

        # Hash provided password
        password_hash = self._hash_password(password, salt)

        # Compare hashes (constant-time comparison)
        return secrets.compare_digest(password_hash, auth_data["password_hash"])

    def encrypt_file(self, file_path: Path, password: str):
        """Encrypt a file"""
        if not self.authenticate(password):
            raise PermissionError("Authentication failed")

        # Load salt
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

        # Derive key
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        # Read file
        with open(file_path, "rb") as f:
            data = f.read()

        # Encrypt
        encrypted_data = fernet.encrypt(data)

        # Write encrypted file
        encrypted_path = self.vault_dir / f"{file_path.name}.enc"
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)
        os.chmod(encrypted_path, 0o600)

        return encrypted_path

    def decrypt_file(self, encrypted_path: Path, password: str) -> bytes:
        """Decrypt a file"""
        if not self.authenticate(password):
            raise PermissionError("Authentication failed")

        # Load salt
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

        # Derive key
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        # Read encrypted file
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        # Decrypt
        return fernet.decrypt(encrypted_data)

    def lock_workspace(self, workspace_path: Path, password: str):
        """Encrypt entire workspace"""
        print(f"🔒 Locking workspace: {workspace_path}")

        encrypted_files = []
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                # Skip already encrypted files
                if file_path.suffix == ".enc":
                    continue

                try:
                    encrypted_path = self.encrypt_file(file_path, password)
                    encrypted_files.append(encrypted_path)
                    print(f"  ✓ Encrypted: {file_path.name}")
                except Exception as e:
                    print(f"  ✗ Failed: {file_path.name} ({e})")

        print(f"\n✓ Locked {len(encrypted_files)} files")
        print(f"✓ Vault location: {self.vault_dir}")

    def unlock_workspace(self, password: str, output_dir: Path):
        """Decrypt entire workspace"""
        print(f"🔓 Unlocking workspace to: {output_dir}")

        decrypted_files = []
        for encrypted_path in self.vault_dir.glob("*.enc"):
            try:
                data = self.decrypt_file(encrypted_path, password)

                # Write decrypted file
                original_name = encrypted_path.stem
                output_path = output_dir / original_name
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(data)

                decrypted_files.append(output_path)
                print(f"  ✓ Decrypted: {original_name}")
            except Exception as e:
                print(f"  ✗ Failed: {encrypted_path.name} ({e})")

        print(f"\n✓ Unlocked {len(decrypted_files)} files")


def main():
    vault = SecureVault()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python secure_vault.py init              # Initialize vault")
        print("  python secure_vault.py lock <path>       # Lock workspace")
        print("  python secure_vault.py unlock <path>     # Unlock workspace")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        password = getpass.getpass("Enter vault password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("✗ Passwords don't match")
            sys.exit(1)

        vault.initialize(password)

    elif command == "lock":
        if len(sys.argv) < 3:
            print("✗ Usage: python secure_vault.py lock <workspace_path>")
            sys.exit(1)

        workspace_path = Path(sys.argv[2])
        password = getpass.getpass("Enter vault password: ")

        vault.lock_workspace(workspace_path, password)

    elif command == "unlock":
        if len(sys.argv) < 3:
            print("✗ Usage: python secure_vault.py unlock <output_path>")
            sys.exit(1)

        output_path = Path(sys.argv[2])
        password = getpass.getpass("Enter vault password: ")

        vault.unlock_workspace(password, output_path)

    else:
        print(f"✗ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
