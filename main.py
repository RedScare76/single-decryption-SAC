import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_aes_base64(ciphertext_b64: str, password: str) -> str:
    ciphertext = base64.b64decode(ciphertext_b64)
    key_16 = password.encode("utf-8")[:16]
    cipher = AES.new(key_16, AES.MODE_ECB)
    decrypted = cipher.decrypt(ciphertext)
    try:
        decrypted = unpad(decrypted, AES.block_size)
    except ValueError:
        pass
    return decrypted.decode("utf-8", errors="replace")

def main():
    username = input("Enter username: ")
    password = input("Enter password: ")
    folder_path = os.path.join("userdata", username)

    first_data = None
    last_data = None

    decrypted_data = []

    for root, dirs, files in os.walk(folder_path):
        for fname in files:
            file_path = os.path.join(root, fname)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

            if not lines:
                continue

            ciphertext_b64 = lines[-1]
            try:
                decrypted_text = decrypt_aes_base64(ciphertext_b64, password)

                try:
                    data = json.loads(decrypted_text)
                    decrypted_data.append(data)
                    print(f"\n--- Decrypted contents of {file_path} ---")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(f"\n[Warning] Could not parse JSON from {file_path}.")
                    print("Raw Decrypted Text:\n", decrypted_text)

                if first_data is None:
                    first_data = decrypted_text
                last_data = decrypted_text

            except Exception as e:
                print(f"\n[Error] Failed to decrypt {file_path}: {str(e)}")

    with open("cleartextusers.json", "w", encoding="utf-8") as outfile:
        json.dump(decrypted_data, outfile, indent=2, ensure_ascii=False)

    if first_data:
        print("\n--- First Decrypted Data ---")
        print(first_data)
    if last_data:
        print("\n--- Last Decrypted Data ---")
        print(last_data)

if __name__ == "__main__":
    main()
