#!/usr/bin/env bash
# b3m admin script – run after cfold unfold

> out.txt

echo "=== ruff format & check ===" >> out.txt
ruff format >> out.txt 2>&1
ruff check --fix >> out.txt 2>&1

echo "\n=== git commits ===" >> out.txt

# tests/test_b3_yml_integration.py
git add tests/test_b3_yml_integration.py
git commit tests/test_b3_yml_integration.py -m 'test: fix b3-yml integration test to read the prepared YAML' || true

# admin.sh (self-update)
git add admin.sh
git commit admin.sh -m 'chore: update admin.sh after test fix' || true

echo "\n=== pytest (b3-yml integration) ===" >> out.txt
uv pip install -e ".[dev]" >> out.txt 2>&1
uv run pytest tests/test_b3_yml_integration.py -v >> out.txt 2>&1 || true

echo "\nadmin.sh finished – see out.txt" | tee -a out.txt
