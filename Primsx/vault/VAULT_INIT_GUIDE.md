# PRIMSX VAULT INITIALIZATION

**WATERMARK: PRIMSX-CODEX-BSP-2025**
**Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED**

---

## 🔐 Vault Security

The Primsx vault uses:
- **AES-256-GCM** encryption
- **PBKDF2** key derivation (100,000 iterations)
- **SHA-256** hashing
- **700 permissions** (owner-only access)

---

## 📍 Initialize Your Vault

Run this command to create your encrypted vault:

```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
source ~/claude_enterprise/.venvs/tools_env/bin/activate
python src/vault_manager.py init --vault-dir ./Primsx/vault
```

You'll be prompted to:
1. Enter a master password
2. Confirm the password

**⚠️ IMPORTANT:**
- Choose a strong password (12+ characters)
- Store it securely (password manager recommended)
- This password CANNOT be recovered if lost

---

## 🔑 Using the Vault

### Store a Secret

```bash
python src/vault_manager.py store \
  --key="api_key" \
  --value="your-secret-here" \
  --vault-dir ./Primsx/vault
```

### Retrieve a Secret

```bash
python src/vault_manager.py get \
  --key="api_key" \
  --vault-dir ./Primsx/vault
```

### List All Keys

```bash
python src/vault_manager.py list \
  --vault-dir ./Primsx/vault
```

---

## 🛡️ Security Best Practices

1. **Never commit vault files to git** (already in .gitignore)
2. **Use different passwords** for different environments
3. **Rotate secrets regularly** (every 90 days)
4. **Backup vault files** to encrypted storage
5. **Test vault access** before storing critical secrets

---

## 📂 Vault Files

After initialization, you'll have:

```
Primsx/vault/
├── .vault.db       # Encrypted secrets (AES-256-GCM)
├── .vault.salt     # Cryptographic salt
└── VAULT_INIT_GUIDE.md  # This file
```

**Permissions: 700** (only you can read/write/execute)

---

## 🚨 What to Store in the Vault

**DO store:**
- API keys (OpenAI, Google Cloud, etc.)
- Database passwords
- OAuth tokens
- SSH private keys
- Encryption keys
- Cloud credentials

**DON'T store:**
- Public information
- Configuration files (use .env instead)
- Temporary tokens (use memory/cache)

---

## 🔄 Vault Workflow

### Development

```bash
# Store dev API key
python src/vault_manager.py store --key="dev_api_key" --value="sk-dev-xxx" --vault-dir ./Primsx/vault
```

### Production

```bash
# Store prod API key
python src/vault_manager.py store --key="prod_api_key" --value="sk-prod-xxx" --vault-dir ./Primsx/vault
```

### CI/CD

```bash
# Retrieve in scripts
API_KEY=$(python src/vault_manager.py get --key="prod_api_key" --vault-dir ./Primsx/vault)
export API_KEY
```

---

## 🆘 Troubleshooting

### "Vault not initialized"
Run the init command above.

### "Decryption failed"
You entered the wrong password. Try again.

### "Permission denied"
Run: `chmod 700 ~/claude_enterprise/workspace/PRIMAX-ai/Primsx/vault`

### Lost password?
There's no way to recover. You'll need to re-initialize (loses all secrets).

---

## 📞 Support

**Email:** kiliaan@bakerstreet221b.store
**GitHub:** https://github.com/Bakery-street-project/PRIMAX-ai

---

**WATERMARK: PRIMSX-CODEX-BSP-2025**

Generated: 2025-12-25
