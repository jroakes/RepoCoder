# RepoCoder

⚠️ **IMPORTANT ALERT** ⚠️

**This tool sends all Python file code in your current folder to a third-party Large Language Model (LLM) via API. It is intended for use with small-ish Python projects only.  It can be adapted for other languages easily.  Currently Anthropic supports 200k tokens of context and Gemini supports 2M. For most small projects this is plenty. You will need to modify if using for larger projects. **

---

RepoCoder is a powerful tool that allows you to analyze and modify your entire code repository using Large Language Models (LLMs) such as Anthropic's Claude or Google's Gemini. It's designed to run in a Jupyter notebook environment, making it easy to review, improve, and refactor your code.

Colab Example: [Notebook](https://colab.research.google.com/drive/1vUIJW1VUWOZbsnAV1WINyNUl6ZSueire#scrollTo=htOxfJ_gIOJs)


## Features

- Crawl and analyze your entire code repository
- Generate a structured representation of your project
- Send code for review, improvement, completion, or correction to LLMs
- Support for both Anthropic's Claude and Google's Gemini models
- Easy-to-use interface within Jupyter notebooks

## Installation

You can install RepoCoder using pip:

```
pip install repocoder
```

## Dependencies

RepoCoder requires the following dependencies:

- google-generativeai
- python-dotenv
- anthropic

You can install these dependencies manually or they will be automatically installed when you install RepoCoder.

## Usage

1. Import RepoCoder in your Jupyter notebook:

```python
from repocoder import send_for_review, print_options
```

2. Set up your environment variables for API keys:

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key"
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key"
```

3. View available options:

```python
print_options()
```

4. Send your code for review or other actions:

```python
action = "code-review"
send_for_review(action, llm="anthropic")  # or llm="gemini"
```

## Using RepoCoder with Visual Studio Code

If you prefer to use Visual Studio Code (VS Code) as your development environment, you can still use RepoCoder with Jupyter notebooks. To do this:

1. Install the [Jupyter extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).
2. Open your `.ipynb` file in VS Code.
3. You can now run RepoCoder directly within VS Code's Jupyter notebook interface.

The Jupyter extension for VS Code provides an integrated notebook experience, allowing you to edit and run Jupyter notebooks directly in your VS Code environment.

## Quick Start with Jupyter Notebook

We provide a Jupyter notebook for easy use of RepoCoder. You can download it directly from our repository:

[Download RepoCoder.ipynb](https://raw.githubusercontent.com/yourusername/repocoder/main/RepoCoder.ipynb)

To use it:

1. Download the notebook and place it in your project directory.
2. Open the notebook in Jupyter or VS Code with the Jupyter extension.
3. Run `!pip install repocoder` in the first cell to install RepoCoder.
4. Follow the instructions in the notebook to analyze your code repository.

## Example

Here's a quick example of how to use RepoCoder:

```python
from repocoder import send_for_review, print_options

# View available options
print_options()

# Define your action
action = "Please review the following code and provide suggestions or identify any errors."

# Send for review using Anthropic's Claude
send_for_review(action, llm="anthropic")

# Or, send for review using Google's Gemini
# send_for_review(action, llm="gemini")
```

## Contributing

We welcome contributions to RepoCoder! Please feel free to submit issues, fork the repository and send pull requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for their Claude API
- Google for their Generative AI API