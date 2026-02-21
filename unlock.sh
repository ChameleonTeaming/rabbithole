#!/bin/bash
# Script to unlock and mount the encrypted vault

echo "Unlocking encrypted vault..."
echo "Please enter your vault password below:"

cryptsetup luksOpen /root/encrypted.img my_encrypted_vault
mount /dev/mapper/my_encrypted_vault /root/EncryptedVault

echo ""
echo "Success! Vault is unlocked and mounted at /root/EncryptedVault"
