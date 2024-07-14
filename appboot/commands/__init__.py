import typer
import uvicorn

from appboot.asgi import get_asgi_application
from appboot.commands.startproject import create_project

app = typer.Typer()


@app.command()
def startproject(project_name: str):
    """
    Create a new Django project with the specified name.
    """
    create_project(project_name)


@app.command()
def startapp(app_name: str):
    """
    Create a new Django project with the specified name.
    """
    print(app_name)


@app.command()
def runserver():
    app = get_asgi_application()
    uvicorn.run(app)
