import os
from google.genai import types


def get_files_info(working_directory, directory="."):
    abs_working = os.path.abspath(working_directory)
    abs_full = os.path.abspath(os.path.join(working_directory, directory))
    if not abs_full.startswith(abs_working):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(abs_full):
        return f'Error: "{directory}" is not a directory'
    try:
        list_of_contents = os.listdir(abs_full)
        lines = []
        for name in list_of_contents:
            path_name = os.path.join(abs_full, name)
            path_size = os.path.getsize(path_name)
            path_status = os.path.isdir(path_name)
            lines.append(f'- {name}: file_size={path_size} bytes, is_dir={path_status}')
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)