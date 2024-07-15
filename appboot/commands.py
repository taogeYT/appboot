import os
import shutil

import typer
import uvicorn
from jinja2 import Environment, FileSystemLoader

import appboot
from appboot.asgi import get_asgi_application
from appboot.utils import snake_to_pascal

app = typer.Typer()


def get_template_path(template_name):
    return os.path.join(appboot.__path__[0], "conf", template_name)


def create_project(project_name: str):
    template_dir = get_template_path("project_template")
    target_dir = project_name
    kwargs = {"project_name": project_name}

    if os.path.exists(target_dir):
        typer.echo(f"Error: Directory {target_dir} already exists.")
        raise typer.Exit()

    shutil.copytree(template_dir, target_dir)
    render_templates("project", target_dir, project_name, kwargs)
    typer.echo(f"Project {project_name} created successfully.")


def create_app(app_name: str, project_dir: str):
    template_dir = get_template_path("app_template")
    target_dir = os.path.join(project_dir, app_name)
    kwargs = {"app_name": app_name, "camel_case_app_name": snake_to_pascal(app_name)}

    if os.path.exists(target_dir):
        typer.echo(f"Error: Directory {target_dir} already exists.")
        raise typer.Exit()

    shutil.copytree(template_dir, target_dir)
    render_templates("app", target_dir, app_name, kwargs)
    typer.echo(f"App {app_name} created successfully in {project_dir}.")


def render_templates(
    app_or_project: str, target_dir: str, name: str, kwargs: dict[str, str]
) -> None:
    env = Environment(loader=FileSystemLoader(target_dir), autoescape=True)

    # 处理文件内容中的占位符
    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if filename.endswith(".j2"):
                with open(file_path, "r") as file:
                    template = env.from_string(file.read())
                rendered_content = template.render(**kwargs)
                new_file_path = os.path.join(root, filename[:-3])  # 去掉 .j2 扩展名
                with open(new_file_path, "w") as file:
                    file.write(rendered_content)
                os.remove(file_path)

    if app_or_project == "project":
        # 处理目录和文件名中的占位符
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for dir_name in dirs:
                new_name = dir_name.replace("project_name", name)
                os.rename(os.path.join(root, dir_name), os.path.join(root, new_name))


@app.command()
def startproject(project_name: str):
    """
    Create a new project with the specified name.
    """
    create_project(project_name)


@app.command()
def startapp(app_name: str, project_dir: str = "."):
    """
    Create a new app with the specified name in the given project directory.
    """
    create_app(app_name, project_dir)


@app.command()
def runserver():
    app = get_asgi_application()
    uvicorn.run(app)
