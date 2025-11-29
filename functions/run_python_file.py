import os
import subprocess
from google.genai import types

schema_run_python_file_info = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute python files with optional arguments. Function is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The .py executable, relative to the working directory. If not provided, an error message is returned. If not a python file, an error message is returned. If successful, you get some or all of stdout, stderr, a no output message and a return code"
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="The optional arguments"
            ),
        },
    ),
)       

def run_python_file(working_directory, file_path, args=[]):
    arguments = args
    abs_working = os.path.abspath(working_directory)
    abs_full = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_full.startswith(abs_working):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_full):
        return f'Error: File "{file_path}" not found.'
    if not abs_full.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        output_parts = []
        process_list = ["python", abs_full, *arguments]
        result = subprocess.run(process_list, timeout=30, capture_output=True, text=True, cwd=abs_working)
        stdout = result.stdout
        stderr = result.stderr
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if result.returncode != 0:
            output_parts.append(f'Process exited with code {result.returncode}')
        if not output_parts:
            return "No output produced."
        return "\n".join(output_parts)

    except Exception as e:
        return f'Error: executing Python file: {e}'






