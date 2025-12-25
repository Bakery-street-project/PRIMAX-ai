#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PRIMAX AI - VAULT MANAGER                           ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-VAULT-BSP-2025                                          ║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import getpass


class PrimaxVault:
    """
    Encrypted vault for PRIMAX AI secrets

    Features:
    - AES-256-GCM encryption
    - PBKDF2 key derivation
    - Zero-knowledge architecture
    - Integration with WEB3_KEYVAULT
    """

    WATERMARK = "PRIMAX-AI-VAULT-BSP-2025"
    VERSION = "1.0.0"
    ITERATIONS = 100_000

    def __init__(self, vault_dir: str = "./vault"):
        """Initialize vault"""
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(exist_ok=True)

        self.vault_file = self.vault_dir / ".vault.db"
        self.salt_file = self.vault_dir / ".vault.salt"

        print(f"🔐 PRIMAX Vault initialized at {self.vault_dir}")

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def initialize(self, password: Optional[str] = None) -> bool:
        """Initialize new vault"""
        if self.vault_file.exists():
            print("⚠️  Vault already exists")
            return False

        if not password:
            password = getpass.getpass("Enter master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            if password != confirm:
                print("❌ Passwords don't match")
                return False

        # Generate salt
        salt = secrets.token_bytes(32)
        self.salt_file.write_bytes(salt)

        # Create empty vault
        empty_vault = {
            "watermark": self.WATERMARK,
            "version": self.VERSION,
            "created": __import__('datetime').datetime.now().isoformat(),
            "secrets": {}
        }

        self._encrypt_and_save(empty_vault, password, salt)

        print("✅ Vault initialized successfully")
        print(f"   Salt: {base64.b64encode(salt[:8]).decode()}...")
        print(f"   Watermark: {self.WATERMARK}")
        return True

    def _encrypt_and_save(self, data: Dict, password: str, salt: bytes):
        """Encrypt and save vault data"""
        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)

        # Generate nonce
        nonce = secrets.token_bytes(12)

        # Encrypt
        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Save
        vault_data = {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode()
        }

        self.vault_file.write_text(json.dumps(vault_data, indent=2))

    def _decrypt_and_load(self, password: str) -> Optional[Dict]:
        """Decrypt and load vault data"""
        if not self.vault_file.exists() or not self.salt_file.exists():
            print("❌ Vault not initialized")
            return None

        try:
            salt = self.salt_file.read_bytes()
            key = self._derive_key(password, salt)
            aesgcm = AESGCM(key)

            vault_data = json.loads(self.vault_file.read_text())
            nonce = base64.b64decode(vault_data["nonce"])
            ciphertext = base64.b64decode(vault_data["ciphertext"])

            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            data = json.loads(plaintext.decode())

            # Verify watermark
            if data.get("watermark") != self.WATERMARK:
                print("⚠️  Warning: Watermark mismatch")

            return data
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return None

    def store(self, key: str, value: Any, password: Optional[str] = None) -> bool:
        """Store secret in vault"""
        if not password:
            password = getpass.getpass("Enter vault password: ")

        vault_data = self._decrypt_and_load(password)
        if not vault_data:
            return False

        vault_data["secrets"][key] = value

        salt = self.salt_file.read_bytes()
        self._encrypt_and_save(vault_data, password, salt)

        print(f"✅ Secret '{key}' stored")
        return True

    def retrieve(self, key: str, password: Optional[str] = None) -> Optional[Any]:
        """Retrieve secret from vault"""
        if not password:
            password = getpass.getpass("Enter vault password: ")

        vault_data = self._decrypt_and_load(password)
        if not vault_data:
            return None

        value = vault_data["secrets"].get(key)
        if value:
            print(f"✅ Retrieved '{key}'")
        else:
            print(f"❌ Secret '{key}' not found")

        return value

    def list_keys(self, password: Optional[str] = None) -> list:
        """List all secret keys"""
        if not password:
            password = getpass.getpass("Enter vault password: ")

        vault_data = self._decrypt_and_load(password)
        if not vault_data:
            return []

        return list(vault_data["secrets"].keys())


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="PRIMAX AI Vault Manager")
    parser.add_argument("command", choices=["init", "store", "get", "list"])
    parser.add_argument("--key", help="Secret key name")
    parser.add_argument("--value", help="Secret value")
    parser.add_argument("--vault-dir", default="./vault", help="Vault directory")

    args = parser.parse_args()

    vault = PrimaxVault(vault_dir=args.vault_dir)

    if args.command == "init":
        vault.initialize()
    elif args.command == "store":
        if not args.key or not args.value:
            print("❌ --key and --value required")
            return
        vault.store(args.key, args.value)
    elif args.command == "get":
        if not args.key:
            print("❌ --key required")
            return
        value = vault.retrieve(args.key)
        if value:
            print(f"{value}")
    elif args.command == "list":
        keys = vault.list_keys()
        print(f"Vault keys ({len(keys)}):")
        for key in keys:
            print(f"  - {key}")


if __name__ == "__main__":
    main()
