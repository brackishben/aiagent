import os
from google.genai import types

def write_file(working_directory, file_path, content):
    abs_working = os.path.abspath(working_directory)
    abs_full = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_full.startswith(abs_working):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        dir_path = os.path.dirname(abs_full)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    except Exception as e:
        return f"Error: {e}"
    try:
        with open(abs_full, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"
    
schema_write_file_info = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite to a file. Function is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to which the content should be written or overwritten, relative to the working directory. If not provided, an error message is returned. If successful, a success message is returned"
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content that should be written to the file"
            ),
        },
    ),
)       