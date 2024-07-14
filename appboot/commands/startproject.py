import os
import shutil

import typer
from jinja2 import Environment, FileSystemLoader

import appboot


def get_template_path(template_name):
    return os.path.join(appboot.__path__[0], "conf", template_name)


def create_project(project_name: str):
    template_dir = get_template_path("project_template")
    target_dir = project_name

    if os.path.exists(target_dir):
        typer.echo(f"Error: Directory {target_dir} already exists.")
        raise typer.Exit()

    shutil.copytree(template_dir, target_dir)
    replace_placeholder(target_dir, project_name)
    typer.echo(f"Project {project_name} created successfully.")


def replace_placeholder(target_dir: str, project_name: str):
    env = Environment(loader=FileSystemLoader(target_dir), autoescape=True)
    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if filename.endswith(".j2"):
                with open(file_path, "r") as file:
                    content = file.read()
                template = env.from_string(content)
                rendered_content = template.render(project_name=project_name)
                new_file_path = os.path.join(root, filename[:-3])
                with open(new_file_path, "w") as file:
                    file.write(rendered_content)
                os.remove(file_path)

    # 处理目录和文件名中的占位符
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for name in dirs:
            new_name = name.replace("project_name", project_name)
            os.rename(os.path.join(root, name), os.path.join(root, new_name))
