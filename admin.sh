#!/bin/bash

# Modified files
FILES=(
    "src/b3m/cli/__init__.py"
    "admin.sh"
)

# Run ruff format
echo "Running ruff format..."
ruff format

# Run ruff check --fix and pipe to out.txt
echo "Running ruff check --fix..."
ruff check --fix > out.txt

# Run pytest and append to out.txt
echo "Running pytest..."
uv run pytest -v >> out.txt

# Commit each file
echo "Committing files..."
for file in "${FILES[@]}"; do
    if [ "$file" == "admin.sh" ]; then
        git add "$file"
        git commit "$file" -m "Add admin.sh script for automated checks and commits"
    else
        git commit "$file" -m "Fix import path for b3_msh.cli.cli app in CLI"
    fi
done
