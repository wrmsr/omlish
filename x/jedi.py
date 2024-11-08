import jedi

def find_method_references(file_path: str, line: int, column: int):
    """
    Finds references to a class method using the jedi library.

    Args:
        file_path (str): Path to the file where the class method is defined.
        line (int): Line number of the method definition.
        column (int): Column number of the method definition.
    """
    with open(file_path, 'r') as file:
        code = file.read()

    # Initialize a Jedi Script object
    script = jedi.Script(code, path=file_path)

    # Get references to the symbol at the specified position
    references = script.get_references(line, column, include_builtins=False)

    # Print out the references found
    print(f"References to method found in '{file_path}':")
    for ref in references:
        print(f"- {ref.module_path}:{ref.line}:{ref.column}: {ref.name}")

# Example usage
if __name__ == "__main__":
    # Adjust the file path, line, and column to match your target method
    find_method_references(
        file_path='example.py',
        line=10,   # Line number of the method definition
        column=5   # Column number within the method name
    )
