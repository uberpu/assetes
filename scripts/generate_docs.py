import os
import ast
import glob

def parse_file(filepath):
    """
    Parses a python file and returns a summary of its classes, functions, and docstrings.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read())

    classes = []
    functions = []

    for element in node.body:
        if isinstance(element, ast.ClassDef):
            class_info = {
                'name': element.name,
                'docstring': ast.get_docstring(element) or "No docstring provided.",
                'methods': []
            }
            for n in element.body:
                if isinstance(n, ast.FunctionDef):
                    class_info['methods'].append({
                        'name': n.name,
                        'docstring': ast.get_docstring(n) or "No docstring provided."
                    })
            classes.append(class_info)
        elif isinstance(element, ast.FunctionDef):
            functions.append({
                'name': element.name,
                'docstring': ast.get_docstring(element) or "No docstring provided."
            })

    return {'classes': classes, 'functions': functions}

def generate_markdown(parsed_data, filename):
    """
    Generates a Markdown string from the parsed AST data.
    """
    md = f"# Documentation for `{filename}`\n\n"

    if parsed_data['classes']:
        md += "## Classes\n\n"
        for c in parsed_data['classes']:
            md += f"### `{c['name']}`\n"
            md += f"{c['docstring']}\n\n"
            if c['methods']:
                md += "**Methods:**\n\n"
                for m in c['methods']:
                    md += f"- **`{m['name']}`**: {m['docstring']}\n"
            md += "\n"

    if parsed_data['functions']:
        md += "## Functions\n\n"
        for f in parsed_data['functions']:
            md += f"### `{f['name']}`\n"
            md += f"{f['docstring']}\n\n"

    if not parsed_data['classes'] and not parsed_data['functions']:
        md += "_No classes or functions found in this file._\n"

    return md

if __name__ == "__main__":
    print("Starting Documentation Generation...")

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_dir, 'docs')

    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # Find all python files in the projects directory
    search_path = os.path.join(project_dir, 'projects', '**', '*.py')
    py_files = glob.glob(search_path, recursive=True)

    for filepath in py_files:
        if '__init__' in filepath:
            continue # skip init files

        relative_path = os.path.relpath(filepath, project_dir)
        filename = os.path.basename(filepath)
        print(f"Parsing {relative_path}...")

        parsed = parse_file(filepath)
        md_content = generate_markdown(parsed, relative_path)

        # Save md file in docs matching the python file name
        doc_filename = filename.replace('.py', '.md')
        doc_filepath = os.path.join(docs_dir, doc_filename)

        with open(doc_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

    print("Documentation Generation Complete!")
