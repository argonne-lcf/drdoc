# Dr. Doc

Dr. Doc is currently a toy but useful project to improve documentation files by identifying and correcting grammar, formatting errors, and broken links using large language models. Currently, this project uses the **Argo API**, which provides access to OpenAI models for Argonne researchers. Future updates will include support for other models, structured output to simplify prompts, as well as GitHub and GitLab actions for continuous integration.

Please note that the current version of gpt4o used by Argo is limited to 4096 output tokens. Therefore, the largest files you can process with Argo/gpt4o are around 15 KB.

## Features

- Fixes grammar, formatting, and link issues in documentation files.
- Supports Markdown (`.md`), reStructuredText (`.rst`), and plain text formats.
- Provides a detailed explanation of changes made to the documentation.
- Optional Git integration to commit changes directly.

## Requirements

- Argo API credentials (`ARGO_URL` and `ARGO_USER` must be defined in the environment)
- Python 3.8 or higher
- `requests>=2.25.0`

## Setup

1. Clone the repository and navigate to the project directory:

   ```bash
   git clone <repository-url>
   cd drdoc
   ```

2. Define the required environment variables for the Argo API:

   ```bash
   export ARGO_URL=<your-argo-url>
   export ARGO_USER=<your-argo-user>
   ```

3. (Optional) Install the package:

   ```bash
   pip install -e .
   ```

## Usage

If you have installed Dr. Doc with pip as described above, you can run it with `drdoc` (`drdoc -h` for help menu). If not, you need to run the Python script with `python <path_to_drdoc>/drdoc.py`.

```bash
drdoc <doc_path> [options]
```

or without installation:

```bash
python <path_to_drdoc>/drdoc.py <doc_path> [options]
```

### Command Line Options

- `doc_path`: (Required) Path to the documentation file or directory containing files to process.
- `--argo_url`: (Optional) Argo API endpoint URL (default: value of `ARGO_URL` environment variable).
- `--argo_user`: (Optional) Argo API user (default: value of `ARGO_USER` environment variable).
- `--model`: (Optional) Model to use (e.g., `gpt4o`, `gpt35`; default: `gpt4o`).
- `--temperature`: (Optional) Sampling temperature for the model (default: 0.1).
- `--top_p`: (Optional) Top-p sampling for the model (default: 0.9).
- `--max_tokens`: (Optional) Max tokens for the prompt (default: 4096).
- `--max_completion_tokens`: (Optional) Max tokens for the completion (default: 16000).
- `--inplace`: (Optional) Modify the original file in place instead of creating a new one.
- `--commit`: (Optional) Commit changes to Git with the explanation as the commit message.
- `--format`: (Optional) Format of the documentation file (`md`, `rst`, or `txt`; default: `md`).

### Example Commands

#### Process a Markdown file:

```bash
drdoc doc/sample.md
```

This would create `doc/sample_fixed.md`.

#### Process all ReStructuredText documentation files (`*.rst` files) in the `doc` directory:

```bash
drdoc doc/ --format rst
```

#### Process a file and modify it in-place:

```bash
drdoc doc/sample.md --inplace
```

#### Process a file in place and commit changes (you need to run it inside the git project):

```bash
cd <your_git_repo>
drdoc README.md --inplace --commit
```

## TODO

- Add support for LangChain to use other models.
- Optionally ask for confirmation for each change.
- Enable using ALCF inference endpoints.
- Add GitHub and GitLab actions to process documentation files for CI.
- Improve the prompts and user experience with feedback.

## Contributing

We welcome contributions to improve Dr. Doc! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.