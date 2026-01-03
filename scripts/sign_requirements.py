import hashlib
import json

def sign_file(path):
    with open(path, "rb") as f:
        data = f.read()

    digest = hashlib.sha256(data).hexdigest()

    signature = {
        "file": path,
        "sha256": digest
    }

    with open(f"{path}.sig.json", "w") as f:
        json.dump(signature, f, indent=2)

if __name__ == "__main__":
    sign_file("requirements.lock")
