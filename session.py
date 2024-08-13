import secrets

# Generate a 32-byte hexadecimal secret key
secret_key = secrets.token_hex(32)
print(secret_key)
