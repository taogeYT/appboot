import os
import shutil
import sys
import traceback

import typer
import uvicorn
from jinja2 import Environment, FileSystemLoader

import appboot
from appboot.conf import settings
from appboot.utils import get_random_secret_key, snake_to_pascal

app = typer.Typer()


def start_ipython():
    from IPython import start_ipython

    start_ipython(argv=[])


def start_python():
    import code

    imported_objects = {}
    # By default, this will set up readline to do tab completion and to read and
    # write history to the .python_history file, but this can be overridden by
    # $PYTHONSTARTUP or ~/.pythonrc.py.
    try:
        hook = sys.__interactivehook__
    except AttributeError:
        # Match the behavior of the cpython shell where a missing
        # sys.__interactivehook__ is ignored.
        pass
    else:
        try:
            hook()
        except Exception:
            # Match the behavior of the cpython shell where an error in
            # sys.__interactivehook__ prints a warning and the exception
            # and continues.
            print('Failed calling sys.__interactivehook__')
            traceback.print_exc()

    # Set up tab completion for objects imported by $PYTHONSTARTUP or
    # ~/.pythonrc.py.
    try:
        import readline
        import rlcompleter

        readline.set_completer(rlcompleter.Completer(imported_objects).complete)
    except ImportError:
        pass

    # Start the interactive interpreter.
    code.interact(local=imported_objects)


def get_template_path(template_name):
    return os.path.join(appboot.__path__[0], 'conf', template_name)


def ensure_target_dir(name, target):
    # if some directory is given, make sure it's nicely expanded
    if not target:
        top_dir = os.path.join(os.getcwd(), name)
        try:
            os.makedirs(top_dir)
        except FileExistsError:
            typer.echo(f"'{top_dir}' already exists")
            raise typer.Exit()
        except OSError as e:
            typer.echo(f'OSError: {e}')
            raise typer.Exit()
    else:
        top_dir = os.path.abspath(os.path.expanduser(target))
        if not os.path.exists(top_dir):
            typer.echo(
                f"Destination directory '{top_dir}' does not exist, please create it first."
            )
            raise typer.Exit()
    return top_dir


def create_project(project_name: str, target_dir: str):
    template_dir = get_template_path('project_template')
    # target_dir = project_name
    kwargs = {'project_name': project_name, 'secret_key': get_random_secret_key()}
    target_dir = ensure_target_dir(project_name, target_dir)
    print(template_dir, target_dir)
    shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)
    render_templates('project', target_dir, project_name, kwargs)
    typer.echo(f'Project {project_name} created successfully.')


def create_app(app_name: str, target: str):
    template_dir = get_template_path('app_template')
    kwargs = {'app_name': app_name, 'camel_case_app_name': snake_to_pascal(app_name)}
    target_dir = ensure_target_dir(app_name, target)
    shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)
    render_templates('app', target_dir, app_name, kwargs)
    typer.echo(f'App {app_name} created successfully.')


def render_templates(
    app_or_project: str, target_dir: str, name: str, kwargs: dict[str, str]
) -> None:
    env = Environment(loader=FileSystemLoader(target_dir), autoescape=True)

    # 处理文件内容中的占位符
    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if filename.endswith('.j2'):
                with open(file_path, 'r') as file:
                    template = env.from_string(file.read())
                rendered_content = template.render(**kwargs)
                new_file_path = os.path.join(root, filename[:-3])  # 去掉 .j2 扩展名
                with open(new_file_path, 'w') as file:
                    file.write(rendered_content)
                os.remove(file_path)

    if app_or_project == 'project':
        # 处理目录和文件名中的占位符
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for dir_name in dirs:
                new_name = dir_name.replace('project_name', name)
                os.rename(os.path.join(root, dir_name), os.path.join(root, new_name))


@app.command()
def startproject(
    name: str = typer.Argument(..., help='Name of the project.'),
    directory: str = typer.Argument('', help='Optional destination directory'),
):
    """
    Create a new project with the specified name.
    """
    create_project(name, directory)


@app.command()
def startapp(
    name: str = typer.Argument(..., help='Name of the application.'),
    directory: str = typer.Argument('', help='Optional destination directory'),
):
    """
    Create a new app with the specified name in the given project directory.
    """
    create_app(name, directory)


@app.command()
def runserver(host: str = '127.0.0.1', port: int = 8000, reload: bool = True):
    asgi = f'{settings.PROJECT_NAME}.asgi:application'
    uvicorn.run(asgi, host=host, port=port, reload=reload)


@app.command()
def shell():
    for python_shell in [start_ipython, start_python]:
        try:
            return python_shell()
        except ImportError:
            pass
