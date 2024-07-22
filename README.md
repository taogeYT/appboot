# appboot
App Boot is a FastAPI project template, Designed to provide a Django-like structure and development experience.

# Installation
Require Python 3.9+
```shell
pip install appboot
```

# Quick start
Startup up a new project
```shell
# Create the project directory
mkdir mysite
cd mysite

# Create a virtual environment to isolate our package dependencies locally
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Set up a new project with a single application
appboot startproject mysite .  # Note the trailing '.' character

# start runserver Application running on http://127.0.0.1:8000
python3 manage.py runserver
```
Startup up a new app
```shell
python3 manage.py startapp polls
```
# Try out examples
Go to [Examples](./examples)
