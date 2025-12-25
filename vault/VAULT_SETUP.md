# PRIMAX AI Encrypted Vault

## Purpose

This vault stores encrypted credentials, API keys, and sensitive configuration for PRIMAX AI.

## Encryption

- **Algorithm**: AES-256-GCM
- **Key Derivation**: PBKDF2 with SHA-256
- **Salt**: Randomly generated per vault
- **Iterations**: 100,000

## Setup

```bash
# Initialize vault (first time)
python src/vault_manager.py init

# Store secret
python src/vault_manager.py store --key="api_key" --value="your_secret"

# Retrieve secret
python src/vault_manager.py get --key="api_key"
```

## Security Notes

1. Never commit `.vault.db` or `.vault.key` to version control
2. Backup your master password securely
3. Use environment variables for production deployment
4. Rotate keys every 90 days

## Integration with WEB3_KEYVAULT

For permanent blockchain storage, PRIMAX AI integrates with Smoothoperator's WEB3_KEYVAULT:

- Master keys stored on Arweave (permanent, immutable)
- Password-protected decryption
- Zero-knowledge architecture
