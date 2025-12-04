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

    max_iterations = 20

    for iteration in range(max_iterations):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                )
            )

            # Add each candidate's content to messages
            for candidate in response.candidates:
                messages.append(candidate.content)

            # Check if the model is finished (no function calls and has text response)
            has_function_calls = any(
                candidate.content.parts and
                any(part.function_call for part in candidate.content.parts)
                for candidate in response.candidates
            )

            if not has_function_calls and response.text:
                print(response.text)
                if verbose:
                    print(f"\nUser prompt: {user_prompt}")
                    print(f"Iterations: {iteration + 1}")
                    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
                break

            # If there are function calls, process them
            if has_function_calls:
                function_responses = []

                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if part.function_call:
                            function_call_result = call_function(part.function_call, verbose=verbose)

                            if (
                                not function_call_result.parts
                                or not function_call_result.parts[0].function_response
                                or not function_call_result.parts[0].function_response.response
                            ):
                                raise RuntimeError("Function call did not return a valid response")

                            function_responses.append(function_call_result.parts[0])

                # Add function responses as a user message
                if function_responses:
                    messages.append(types.Content(role="user", parts=function_responses))

                    if verbose:
                        print(f"-> Function responses added to conversation")

        except Exception as e:
            print(f"Error during generation: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            break

    else:
        # Loop completed without breaking (max iterations reached)
        print(f"Maximum iterations ({max_iterations}) reached without completion.")

if __name__ == "__main__":
    main()
