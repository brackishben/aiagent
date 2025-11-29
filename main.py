import os
import sys
from dotenv import load_dotenv
from call_function import call_function
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_content_info
from functions.write_file import schema_write_file_info
from functions.run_python_file import schema_run_python_file_info

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Write or overwrite files
- Execute Python files with optional arguments

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_content_info,
        schema_write_file_info,
        schema_run_python_file_info
    ]
)

def main():
    
    if len(sys.argv) < 2:
        print("No query was entered, please run again with a query")
        sys.exit(1)
    user_prompt = sys.argv[1]
    verbose = "--verbose" in sys.argv
    messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], 
            system_instruction=system_prompt
            )
        )
    if not response.function_calls:
        print(response.text)

    function_responses = []
        
    for item in response.function_calls:
        function_call_result = call_function(item, verbose=verbose)

        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
            or not function_call_result.parts[0].function_response.response
        ):
            raise RuntimeError("Function call did not return a valid response")
        
        function_responses.append(function_call_result.parts[0])
    
    if verbose:
        print(f"-> {function_call_result.parts[0].function_response.response}")
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()
