import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import anthropic
import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
from IPython.display import display, Markdown # type: ignore
from dotenv import load_dotenv
import re
import fnmatch
import chardet

load_dotenv()

# Default exclusion lists
DEFAULT_EXCLUDE_DIRS = [
    ".git",
    "__pycache__",
    "venv",
    "docs",
    "build",
    "dist",
]

DEFAULT_EXCLUDE_FILES = [
    "setup.py",
    "requirements.txt",
    ".env"
]

DEFAULT_EXCLUDE_EXTENSIONS = [
    ".pyc",
    ".pyo",
    ".pyd"
]

def process_gitignore(directory: str = ".") -> Tuple[List[str], List[str], List[str]]:
    """Processes .gitignore and returns lists of patterns for excluded dirs, files, and extensions.
    
    Args:
        directory: The directory to process.
        
    Returns:
        A tuple containing lists of excluded directories, files, and extensions.
    """
    
    exclude_dirs: List[str] = []
    exclude_files: List[str] = []
    exclude_extensions: List[str] = []

    # Check both local and root .gitignore files
    gitignore_paths = [
        Path(directory) / ".gitignore",
        Path(directory).resolve().parent / ".gitignore"
    ]

    for gitignore_path in gitignore_paths:
        try:
            if gitignore_path.exists():
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if line.endswith("/"):
                                # Directory pattern
                                exclude_dirs.append(line[:-1])
                            elif line.startswith("*."):
                                # Extension pattern
                                exclude_extensions.append(line.replace("*", ""))
                            elif "*" in line:
                                # Wildcard pattern for files
                                exclude_files.append(line)
                            else:
                                # Specific file or directory
                                exclude_files.append(line)
        except IOError as e:
            print(f"Warning: Error reading {gitignore_path}: {e}", file=sys.stderr)
            continue

    return exclude_dirs, exclude_files, exclude_extensions


def crawl_directory(
    directory: str = ".",
    additional_exclude_extensions: Optional[List[str]] = None,
    additional_exclude_dirs: Optional[List[str]] = None,
    additional_exclude_files: Optional[List[str]] = None,
    gitignore_exclude_dirs: Optional[List[str]] = None,
    gitignore_exclude_files: Optional[List[str]] = None,
    gitignore_exclude_extensions: Optional[List[str]] = None,
    use_default_exclusions: bool = True,
) -> Tuple[List[Tuple[str, Optional[List]]], List[str]]:
    """Crawls a directory and returns a list of file paths and directory structure.

    Args:
        directory: The directory to crawl.
        additional_exclude_extensions: Additional file extensions to exclude.
        additional_exclude_dirs: Additional directories to exclude.
        additional_exclude_files: Additional files to exclude.
        gitignore_exclude_dirs: Directories to exclude from .gitignore.
        gitignore_exclude_files: Files to exclude from .gitignore.
        gitignore_exclude_extensions: Extensions to exclude from .gitignore.
        use_default_exclusions: Whether to use the default exclusion lists.

    Returns:
        A tuple containing the directory structure and a list of Python file paths.
    """
    # Initialize exclusion lists based on use_default_exclusions
    exclude_extensions = (DEFAULT_EXCLUDE_EXTENSIONS if use_default_exclusions else []) + (
        additional_exclude_extensions or []
    ) + (gitignore_exclude_extensions or [])

    exclude_dirs = (DEFAULT_EXCLUDE_DIRS if use_default_exclusions else []) + (
        additional_exclude_dirs or []
    ) + (gitignore_exclude_dirs or [])

    exclude_files = (DEFAULT_EXCLUDE_FILES if use_default_exclusions else []) + (
        additional_exclude_files or []
    ) + (gitignore_exclude_files or [])

    structure: List[Tuple[str, Optional[List]]] = []
    files: List[str] = []

    try:
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [
                d
                for d in dirs
                if d not in exclude_dirs and not any(fnmatch.fnmatch(d, pattern) for pattern in gitignore_exclude_dirs or [])
            ]

            rel_path = os.path.relpath(root, directory)
            if rel_path != ".":
                structure.append((rel_path, []))

            for filename in filenames:
                if filename not in exclude_files and not any(
                    filename.endswith(ext) for ext in exclude_extensions
                ) and not any(fnmatch.fnmatch(filename, pattern) for pattern in gitignore_exclude_extensions or []):

                    file_path = os.path.join(root, filename)
                    rel_file_path = os.path.relpath(file_path, directory)
                    structure.append((rel_file_path, None))
                    files.append(file_path)
                
    except PermissionError:
        print(f"Permission denied: {directory}")
    except Exception as e:
        print(f"Error accessing {directory}: {e}")

    return structure, files


def generate_tree(
    structure: List[Tuple[str, Optional[List]]], prefix: str = ""
) -> List[str]:
    """Generates a tree-like representation of the directory structure.

    Args:
        structure: The directory structure as returned by crawl_directory.
        prefix: The prefix to use for each line.

    Returns:
        A list of strings representing the directory tree.
    """
    tree: List[str] = []
    for i, (name, substructure) in enumerate(structure):
        is_last = i == len(structure) - 1
        branch = "└── " if is_last else "├── "
        new_prefix = prefix + ("    " if is_last else "│   ")

        tree.append(f"{prefix}{branch}{name}")
        if substructure:
            tree.extend(generate_tree(substructure, new_prefix))
    return tree


def get_code(files: List[str]) -> List[str]:
    """Reads the code from the given files with robust encoding detection.

    Args:
        files: A list of file paths.

    Returns:
        A list of strings, where each string is the content of a file.
    """
    contents = []
    # Common encodings to try first, in order of likelihood
    common_encodings = ['utf-8', 'ascii', 'iso-8859-1', 'windows-1252', 'utf-16']
    
    for file in files:
        content = None
        try:
            # First try reading with common encodings
            for encoding in common_encodings:
                try:
                    with open(file, 'r', encoding=encoding) as f:
                        content = f.read()
                        break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Warning: Error reading {file} with {encoding}: {e}", file=sys.stderr)
                    continue
            
            # If common encodings fail, use chardet
            if content is None:
                # Read file in chunks to handle large files
                chunk_size = 1024 * 1024  # 1MB chunks
                raw_data = b''
                
                with open(file, 'rb') as f:
                    chunk = f.read(chunk_size)
                    if chunk:  # Just read the first chunk for detection
                        raw_data = chunk
                
                if raw_data:
                    detected = chardet.detect(raw_data)
                    if detected and detected['encoding']:
                        try:
                            with open(file, 'r', encoding=detected['encoding']) as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            pass
            
            # Final fallback to latin-1
            if content is None:
                try:
                    with open(file, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error: Final fallback failed for {file}: {e}", file=sys.stderr)
                    content = f"# Error reading file {file}: Unable to determine correct encoding"
            
            contents.append(content)
            
        except MemoryError:
            print(f"Error: File {file} is too large to process", file=sys.stderr)
            contents.append(f"# Error: File {file} is too large to process")
        except Exception as e:
            print(f"Error: Unexpected error reading {file}: {e}", file=sys.stderr)
            contents.append(f"# Error reading file {file}: {str(e)}")
            
    return contents


def write_code(
    files: List[str],
    code: List[str],
    directory_structure: List[str],
    output_file: str = "all_code.txt",
) -> None:
    """Writes the code and directory structure to a file.

    Args:
        files: A list of file paths.
        code: A list of code strings.
        directory_structure: A list of strings representing the directory structure.
        output_file: The name of the output file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Directory Structure:\n")
            f.write("\n".join(directory_structure))
            f.write("\n\nFile Contents:\n\n")
            for file, content in zip(files, code):
                f.write(f"File Path: {file}\nCode:\n{content}\n\n")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)


def format_code_for_llm(
    directory: str = ".",
    output_file: str = "all_code.txt",
    additional_exclude_extensions: Optional[List[str]] = None,
    additional_exclude_dirs: Optional[List[str]] = None,
    additional_exclude_files: Optional[List[str]] = None,
    use_gitignore: bool = True,
    use_default_exclusions: bool = True,
) -> str:
    """Formats the code and directory structure for the LLM.

    Args:
        directory: The directory to process.
        output_file: The name of the output file.
        additional_exclude_extensions: Additional file extensions to exclude.
        additional_exclude_dirs: Additional directories to exclude.
        additional_exclude_files: Additional files to exclude.
        use_gitignore: Whether to use .gitignore file to exclude files and directories.
        use_default_exclusions: Whether to use the default exclusion lists.

    Returns:
        The path to the output file.
    """
    current_dir = Path(directory)

    gitignore_exclude_dirs, gitignore_exclude_files, gitignore_exclude_extensions = [], [], []
    if use_gitignore:
        gitignore_exclude_dirs, gitignore_exclude_files, gitignore_exclude_extensions = process_gitignore(directory)

    structure, files = crawl_directory(
        current_dir,
        additional_exclude_extensions,
        additional_exclude_dirs,
        additional_exclude_files,
        gitignore_exclude_dirs,
        gitignore_exclude_files,
        gitignore_exclude_extensions,
        use_default_exclusions,
    )
    code = get_code(files)

    directory_structure = [str(current_dir.name) + "/"] + generate_tree(structure)

    write_code(files, code, directory_structure, output_file)
    return output_file


def print_options() -> None:
    """Prints the available options for the user."""
    print("Available options:")
    print("1. Code Review. Action: code-review")
    print("2. Code Improvement. Action: code-improvement")
    print("3. Code Completion. Action: code-completion")
    print("4. Code Correction. Action: code-correction")
    print("5. Custom Action. Action: <your custom action>")


def display_markdown_response(response: Optional[str]) -> None:
    """Displays the markdown response from the LLM.

    Args:
        response: The markdown response string.
    """
    if response:
        # Remove '```python' or '```' from the beginning of code blocks
        cleaned_response = re.sub(r"```(?:python)?\n", "```\n", response)

        # Save the response to a file
        with open("response.md", "w", encoding="utf-8") as f:
            f.write(cleaned_response)

        display(Markdown(cleaned_response))
    else:
        print("No response received from the API.")


ACTION_DICT: Dict[str, str] = {
    "code-review": "Please review the following code and provide suggestions or identify any errors.",
    "code-improvement": "Please suggest improvements to the following code.",
    "code-completion": "Please add to the following code by adding limited new files or missing functionality.",
    "code-correction": "Correct the following code by fixing any errors or issues.",
}


def create_prompt(content: str, action: str) -> str:
    """Creates the prompt for the LLM.

    Args:
        content: The code content.
        action: The action to perform.

    Returns:
        The prompt string.
    """
    action_instruction = ACTION_DICT.get(action, action)

    return f"""
    Action: {action_instruction}
    Instructions: You will be given a directory structure followed by a set of Python files in the format: File Path: <file path> Code: <code>. Please apply the Action to each file. Please provide your response in the following format:

    File Path: <file path>

    Changes:
    - <bulleted list of changes/suggestions>

    Updated Code:

    ```
    <full, complete file code>
    ```

    Important: 
    1. Always provide the FULL, UPDATED code for each file that has changes. 
    2. DO NOT use placeholders or omit any parts of the code.
    3. If no changes are required for a file, explicitly state "No changes required." under the Changes section and DO NOT include the "Updated Code" section.
    4. Include ALL comments in the updated code.
    5. Do not use ellipsis (...) or any other shorthand to indicate unchanged code.

    Content:
    {content}
    """


def send_to_anthropic_api(
    content: str,
    action: str = "code-review",
    model: str = "claude-3-5-sonnet-latest",
    api_key: Optional[str] = None,
) -> Optional[str]:
    """Sends the code to the Anthropic API.

    Args:
        content: The code content.
        action: The action to perform.
        model: The Anthropic model to use.
        api_key: The Anthropic API key.

    Returns:
        The response from the API.
    """
    try:
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key not provided. Please provide an API key."
                )

        prompt = create_prompt(content, action)

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.1,
            system="You are a world-class Python developer. Provide complete, error-free code only when changes are made. Include ALL comments in updated code. Never use placeholders or ellipsis. State 'No changes required' without including code if no changes are needed. Format in Markdown with appropriate headers, lists, and code blocks. Use triple backticks for code blocks without language specification. Analyze thoroughly before responding. Provide clear, concise change lists. Follow the exact format in the instructions.",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except anthropic.APIError as e:
        print(f"Anthropic API error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error sending to Anthropic API: {e}", file=sys.stderr)
    return None


def send_to_gemini_api(
    content: str,
    action: str = "code-review",
    model_name: str = "gemini-1.5-pro",
    api_key: Optional[str] = None,
) -> Optional[str]:
    """Sends the code to the Gemini API.

    Args:
        content: The code content.
        action: The action to perform.
        model_name: The Gemini model to use.
        api_key: The Gemini API key.

    Returns:
        The response from the API.
    """
    try:
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Gemini API key not provided. Please provide an API key."
                )

        genai.configure(api_key=api_key)

        system_instruction = [
            "You are a world-class Python developer. Provide complete, error-free code only when changes are made.",
            "Include ALL comments in updated code. Never use placeholders or ellipsis.",
            "State 'No changes required' without including code if no changes are needed.",
            "Format in Markdown with appropriate headers, lists, and code blocks.",
            "Use triple backticks for code blocks without language specification.",
            "Analyze thoroughly before responding. Provide clear, concise change lists.",
            "Follow the exact format in the instructions.",
        ]

        model = GenerativeModel(model_name=model_name)

        prompt = create_prompt(content, action)

        # Combine system instruction and prompt
        full_prompt = "\n".join(system_instruction) + "\n\n" + prompt

        response = model.generate_content(
            full_prompt,
            generation_config=GenerationConfig(
                temperature=0.1, max_output_tokens=8192, response_mime_type="text/plain"
            ),
        )
        return response.text
    except Exception as e:
        print(f"Error sending to Gemini API: {e}", file=sys.stderr)
    return None


def send_for_review(
    action: str = "code-review",
    llm: str = "anthropic",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    directory: str = ".",
    output_file: str = "all_code.txt",
    additional_exclude_extensions: Optional[List[str]] = None,
    additional_exclude_dirs: Optional[List[str]] = None,
    additional_exclude_files: Optional[List[str]] = None,
    use_gitignore: bool = True,
    use_default_exclusions: bool = True,
) -> None:
    """Sends the code for review using the specified LLM.

    Args:
        action: The action to perform.
        llm: The LLM to use ('anthropic' or 'gemini').
        model: The model to use.
        api_key: The API key.
        directory: The directory containing the code.
        output_file: The file to write the formatted code to.
        additional_exclude_extensions: Additional file extensions to exclude.
        additional_exclude_dirs: Additional directories to exclude.
        additional_exclude_files: Additional files to exclude.
        use_gitignore: Whether to use .gitignore file to exclude files and directories.
        use_default_exclusions: Whether to use the default exclusion lists.
    """
    try:
        formatted_code_file = format_code_for_llm(
            directory,
            output_file,
            additional_exclude_extensions,
            additional_exclude_dirs,
            additional_exclude_files,
            use_gitignore,
            use_default_exclusions,
        )

        with open(formatted_code_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content:
            raise ValueError("No content found in the specified directory.")

        if not isinstance(action, str) or len(action) <= 5:
            raise ValueError("Invalid action. Please provide a valid action string.")

        if llm.lower() == "anthropic":
            model = model or "claude-3-5-sonnet-latest"
            response = send_to_anthropic_api(content, action, model, api_key)
        elif llm.lower() == "gemini":
            model = model or "gemini-1.5-pro-002"
            response = send_to_gemini_api(content, action, model, api_key)
        else:
            raise ValueError(
                f"Unsupported LLM: {llm}. Please choose either 'anthropic' or 'gemini'."
            )

        display_markdown_response(response)
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)