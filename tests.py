from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file


print(run_python_file("calculator", "main.py")) #(should print the calculator's usage instructions)
print(run_python_file("calculator", "main.py", ["3 + 5"])) #(should run the calculator... which gives a kinda nasty rendered result)
print(run_python_file("calculator", "tests.py"))
print(run_python_file("calculator", "../main.py")) #(this should return an error)
print(run_python_file("calculator", "nonexistent.py")) #(this should return an error)
print(run_python_file("calculator", "lorem.txt")) #(this should return an error)
