import os

import uvicorn


def main():
    os.environ.setdefault("APP_BOOT_SETTINGS_MODULE", "app_polls.settings")
    from app_polls.router import app

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
