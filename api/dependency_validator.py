import importlib
from fastapi import FastAPI

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "requests",
    "python_dotenv",
    "cryptography",
    "dnspython",
    "rich",
    "tabulate",
    "termcolor",
    "urllib3",
]

def validate_dependencies():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        raise RuntimeError(
            f"Missing required dependencies: {', '.join(missing)}"
        )

def attach_validator(app: FastAPI):
    @app.on_event("startup")
    async def startup_check():
        validate_dependencies()
