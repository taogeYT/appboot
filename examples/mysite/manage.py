#!/usr/bin/env python

import os


def main():
    os.environ.setdefault('APP_BOOT_SETTINGS_MODULE', 'mysite.settings')
    try:
        from appboot.commands import app
    except ImportError as exc:
        raise ImportError(
            "Couldn't import App Boot. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    app()


if __name__ == '__main__':
    main()
