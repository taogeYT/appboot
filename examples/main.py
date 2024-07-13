import os


def main():
    os.environ.setdefault("APP_BOOT_SETTINGS_MODULE", "examples.settings")
    from examples.foo import run

    run()


if __name__ == "__main__":
    main()
