# RepoCoder

⚠️ **IMPORTANT ALERT** ⚠️

**This tool sends most Python file code in your current folder to a third-party Large Language Model (LLM) via API. It is designed for use with limited size Python projects.  It can be adapted for other languages easily by forking and updating the code.  Currently Anthropic supports 200k tokens of context and Gemini supports 2M. For most small projects this is plenty. You will need to modify  to add significant complexity (DAGs, RAG, etc) if using for larger projects. **

RepoCoder is a Python package that allows you to send your code for review using Large Language Models (LLMs) like Anthropic's Claude or Google's Gemini. It provides an easy way to get code reviews, suggestions for improvements, and more.

## Features

- Code review using Anthropic's Claude or Google's Gemini
- Support for various actions: code review, code improvement, code completion, and code correction
- Customizable exclusion of files and directories
- Integration with .gitignore for automatic exclusion of files and directories
- Markdown formatting of LLM responses
- Easy-to-use API

## Installation

You can install RepoCoder using pip:

```
pip install repocoder
```

## Usage

Here's a basic example of how to use RepoCoder:

```
from repocoder import send_for_review, print_options

# Print available options
print_options()

# Send code for review
send_for_review(
    action="code-review",
    llm="anthropic",
    directory="path/to/your/code",
    use_gitignore=True
)
```

### Using .gitignore

RepoCoder now supports using your project's .gitignore file to automatically exclude files and directories from the code review process. To enable this feature, set the `use_gitignore` parameter to `True` when calling `send_for_review`:

```
send_for_review(
    action="code-review",
    llm="anthropic",
    directory="path/to/your/code",
    use_gitignore=True
)
```

This will ensure that any files or directories specified in your .gitignore file are not included in the code review.

### Additional Optional Parameters

The `send_for_review` function supports several optional parameters for fine-tuning the review process:

```
send_for_review(
    action="code-review",
    llm="anthropic",
    model="claude-3-sonnet-20240229",  # Specify the model version
    api_key="your_api_key_here",  # Provide your API key directly
    directory="path/to/your/code",
    output_file="custom_output.txt",  # Specify a custom output file name
    additional_exclude_extensions=[".txt", ".md"],  # Exclude additional file types
    additional_exclude_dirs=["tests", "docs"],  # Exclude additional directories
    additional_exclude_files=["config.ini", "secrets.json"],  # Exclude specific files
    use_gitignore=True
)
```

These parameters allow you to:
- Choose a specific model version
- Provide your API key directly (if not set as an environment variable)
- Customize the output file name
- Exclude additional file types, directories, or specific files
- Enable or disable .gitignore integration

## API Key Setup

To use RepoCoder, you need to set up your API key as an environment variable:

- For Anthropic: `ANTHROPIC_API_KEY`
- For Gemini: `GEMINI_API_KEY`

You can set these environment variables in your shell or use a `.env` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.