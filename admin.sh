#!/bin/bash

# List of files added/modified
files=(
    "src/b3m/cli/__init__.py"
    "examples/build_blade.py"
    "admin.sh"
)

# Run ruff format
ruff format

# Run ruff check and fix, pipe to out.txt
ruff check --fix > out.txt

# Run pytest and append to out.txt
uv run pytest -v >> out.txt

# Commit each file
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "File $file does not exist, skipping."
        continue
    fi
    # Check if new or modified
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        # File is tracked, check if modified
        if ! git diff --quiet "$file"; then
            git commit "$file" -m "summary of edits for $file"
        fi
    else
        # New file
        git add "$file"
        git commit "$file" -m "summary of edits for $file"
    fi
done
