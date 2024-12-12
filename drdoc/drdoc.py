import requests
import json
import os
import argparse
import time
import subprocess

PROMPT = """
Please review the following Markdown file for errors and improvements:

CONTENT

SEPARATOR  

Task Instructions

Your task is to review and improve the provided Markdown file as follows:

1. Grammar: Identify and correct any grammatical errors.
2. Broken Links: Verify all links and fix any that are broken.
3. Formatting: Address any formatting issues to ensure consistency and readability.
4. Headers: Do not modify anchor tags within headers.
5. Explanations: Provide a brief explanation of the changes you made.

Response Format

- If no changes are required, respond with:  "No changes required".
- If changes are required, structure your response in two parts, separated by SEPARATOR on a new line:  
  1. The revised Markdown content.  
  2. A brief explanation of the changes, formatted like a git commit message.

Example Response

# ALCF User Guides  
We are moving our ALCF documentation into GitHub to make it easier to contribute and collaborate on our user and machine guides.  

Our user guides contain information for:  

- [Aurora/Sunspot](https://www.alcf.anl.gov/support-center/aurora-sunspot): Information on getting your code ready for our upcoming exascale supercomputer.  
- [Polaris](polaris/getting-started.md): Information on how to get started with our newest supercomputer.  

## How to Get Access  
Researchers interested in using the ALCF systems (including Polaris and the AI Testbed’s Cerebras CS-2 and SambaNova DataScale platforms) can now submit project proposals via the [ALCF’s Director’s Discretionary program](https://www.alcf.anl.gov/science/directors-discretionary-allocation-program). 

SEPARATOR  

- Corrected a grammatical error in the introduction by changing "collaborate to" to "collaborate on."  
- Fixed a typo in the "Aurora/Sunspot" section by changing "exacale" to "exascale."  
- Added the missing word "with" in the "Polaris" section to improve readability.  
- Corrected a typo in the "How to Get Access" section by changing "porposals" to "proposals."
"""

SYSTEM_PROMPT = """
You are an AI language model designed to assist with reviewing and improving Markdown documentation files. 
Your task is to identify and correct any errors in grammar, broken links, and formatting issues within the content of the file. 
Ensure that the revised Markdown content maintains clarity and accuracy, and adheres to best practices for technical documentation.
Provide a brief explanation of the changes made in a typical git commit format, highlighting the specific improvements and the rationale behind them. 
"""


def prepend_filename_with_fixed(file_path):
    """Create a new file path by prepending '_fixed' to the filename.

    Parameters
    ----------
    file_path : str
        The original file path to modify.

    Returns
    -------
    str
        A new file path with '_fixed' inserted before the file extension.

    Examples
    --------
    >>> prepend_filename_with_fixed('/path/to/file.txt')
    '/path/to/file_fixed.txt'
    """
    # Split the file path into directory and filename
    directory, filename = os.path.split(file_path)

    # Split the filename into name and extension
    name, extension = os.path.splitext(filename)

    # Create the new filename by appending '_fixed' before the extension
    new_filename = f"{name}_fixed{extension}"

    # Join the directory and new filename to create the new path
    new_file_path = os.path.join(directory, new_filename)

    return new_file_path


def process_documentation_file(file_path, args):
    print(f"Processing {file_path}...")
    filename = os.path.basename(file_path)
    # Function to process a single documentation file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = PROMPT.replace("CONTENT", content)
    separator = args.separator
    prompt = prompt.replace("SEPARATOR", separator)
    # Modify the prompt based on the format
    if args.format == "md":
        system_prompt = SYSTEM_PROMPT
    elif args.format == "rst":
        prompt = prompt.replace("Markdown", "reStructuredText")
        system_prompt = SYSTEM_PROMPT.replace("Markdown", "reStructuredText")
    elif args.format == "txt":
        prompt = prompt.replace("Markdown", "text")
        system_prompt = SYSTEM_PROMPT.replace("Markdown", "text")
    else:
        raise ValueError("Unsupported format specified.")

    data = {
        "user": args.argo_user,
        "model": args.model,
        "system": system_prompt,
        "prompt": [prompt],
        "stop": [],
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_completion_tokens": args.max_completion_tokens,
    }

    # Convert the dict to JSON
    payload = json.dumps(data)

    # Add a header stating that the content type is JSON
    headers = {"Content-Type": "application/json"}

    start_time = time.time()

    # Send POST request
    try:
        response = requests.post(args.argo_url, data=payload, headers=headers)
    except Exception as e:
        print(f"Error making POST request: {str(e)}")
        print(f"Arguments: url={args.argo_url}, payload={payload}, headers={headers}")
        raise

    end_time = time.time()  # End timing
    response_time = end_time - start_time
    print(f"Response Time: {response_time:.2f} seconds")

    # Receive the response data
    print("Status Code: ", response.status_code)

    try:
        res = response.json().get("response", "")
    except Exception as e:
        print(f"Error parsing response: {str(e)}")
        print(f"Response content: {response.text}")
        raise
    res_parts = res.split(separator)
    if len(res_parts) == 2:
        fixed_md = res_parts[0].strip()
        # Write the markdown content to the original file or a new file
        if args.inplace:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_md)
            print(f"Documentation file modified inplace at: {file_path}")
        else:
            fixed_md_file = prepend_filename_with_fixed(file_path)
            with open(fixed_md_file, "w", encoding="utf-8") as f:
                f.write(fixed_md)
            print(f"Improved documentation file written at: {fixed_md_file}")
        explanation = res_parts[1].strip()
        print(f"Updates for {filename} with {args.model}: \n{explanation}")

        if args.commit:
            commit_message = f"Updates for {filename} with {args.model} \n{explanation}"
            subprocess.run(["git", "add", file_path], check=True)
            subprocess.run(["git", "commit", "-m", explanation], check=True)
            print("Changes committed to Git.")
    else:
        print("*" * 25)
        print(f" Problem detected, please check response:\n{res}")
        print("*" * 25)


def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="Process documentation files for grammar and formatting improvements."
    )
    parser.add_argument("doc_path", help="Path to the markdown file.")
    parser.add_argument(
        "--argo_url",
        default=os.getenv("ARGO_URL"),
        help="ARGO API endpoint URL.",
    )
    parser.add_argument(
        "--argo_user",
        default=os.getenv("ARGO_USER"),
        help="User for the Argo API request.",
    )
    parser.add_argument(
        "--model", default="gpt4o", help="Model to use (e.g., gpt4o, gpt35)."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Sampling temperature for the model.",
    )
    parser.add_argument(
        "--top_p", type=float, default=0.9, help="Top-p sampling for the model."
    )
    parser.add_argument(
        "--max_tokens", type=int, default=16000, help="Max tokens for the prompt."
    )
    parser.add_argument(
        "--max_completion_tokens",
        type=int,
        default=16000,
        help="Max tokens for the completion.",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Modify the file inplace.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit changes to Git with the explanation as the commit message.",
    )
    parser.add_argument(
        "--format",
        choices=["md", "rst", "txt"],
        default="md",
        help="Format of the documentation file. Use 'md' for Markdown, 'rst' for reStructuredText, and 'txt' for plain text.",
    )
    parser.add_argument(
        "--separator",
        default="------SEPARATOR------",
        help="Separator string to use between content and explanation.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Run main processing function with parsed arguments
    process_main(args)


def process_main(args):
    # Move the existing main logic here
    if os.path.isdir(args.doc_path):
        # If the path is a directory, search for documentation files recursively
        for root, _, files in os.walk(args.doc_path):
            for file in files:
                if file.endswith(f".{args.format}"):  # Check for supported formats
                    file_path = os.path.join(root, file)
                    process_documentation_file(file_path, args)
    else:
        # Process a single documentation file
        process_documentation_file(args.doc_path, args)


if __name__ == "__main__":
    main()
