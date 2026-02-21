#!/bin/bash
# Script to unmount and lock the encrypted vault

echo "Locking encrypted vault..."

umount /root/EncryptedVault
cryptsetup luksClose my_encrypted_vault

echo "Success! Vault is now locked."
