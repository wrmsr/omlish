import os
import glob
from typing import Set, List


def get_dockerfile_referenced_files(dockerfile_content: str, context_dir: str) -> Set[str]:
    """
    Extracts the set of files referenced by a Dockerfile during the build process.

    :param dockerfile_content: The source text of the Dockerfile.
    :param context_dir: The directory where the Dockerfile is located (i.e., the build context).
    :return: A set of absolute file paths that are referenced in the build.
    """
    referenced_files = set()

    for line in dockerfile_content.splitlines():
        line = line.strip()

        # Ignore comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Match COPY or ADD instructions
        if line.startswith(("COPY ", "ADD ")):
            parts = line.split()
            if len(parts) < 3:  # Must have at least: COPY src dst
                continue

            sources = parts[1:-1]  # All but the last argument (destination)

            for src in sources:
                abs_path = os.path.join(context_dir, src)

                # Handle glob patterns
                matched_files = glob.glob(abs_path, recursive=True)

                if os.path.isdir(abs_path):
                    # Expand directory to list all files inside
                    for root, _, files in os.walk(abs_path):
                        for file in files:
                            referenced_files.add(os.path.join(root, file))
                elif matched_files:
                    referenced_files.update(matched_files)
                elif os.path.exists(abs_path):
                    referenced_files.add(abs_path)

    return referenced_files


def _main():
    # Example Usage
    dockerfile_text = """\
# Example Dockerfile
FROM python:3.8
COPY requirements.txt /app/
COPY src/ /app/src/
ADD static/*.html /app/static/
"""
    context_directory = "/path/to/build/context"  # Replace with actual context directory

    referenced_files = get_dockerfile_referenced_files(dockerfile_text, context_directory)
    print(referenced_files)


if __name__ == '__main__':
    _main()