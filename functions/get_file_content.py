import os
from config import MAX_CHARS
from google.genai import types


def get_file_content(working_directory, file_path):
    abs_working = os.path.abspath(working_directory)
    abs_full = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_full.startswith(abs_working):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_full):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(abs_full, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if os.path.getsize(abs_full) > MAX_CHARS:
                return file_content_string + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return file_content_string
    except Exception as e:
        return f"Error: {e}"
    
schema_get_content_info = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of the specified file. Function is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to read the contents of, relative to the working directory. If not provided, an error message is returned. File output is truncated to a MAX number of characters",
            ),
        },
    ),
)    