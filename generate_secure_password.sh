#!/bin/bash
NEW_PW=$(openssl rand -base64 32)
echo "VAULT_PASSWORD=$NEW_PW" > ~/.primax_vault_password
chmod 600 ~/.primax_vault_password
echo "✓ New secure password generated"
echo "✓ Saved to: ~/.primax_vault_password"
echo ""
echo "View it with: cat ~/.primax_vault_password"
echo "IMPORTANT: Save this password in your password manager!"
echo ""
cat ~/.primax_vault_password
