import argparse
import sys


def main():
    """Manage sources in pyproject.toml: enforce Git, switch to local, or toggle between modes."""
    parser = argparse.ArgumentParser(description="Manage sources in pyproject.toml for active dependencies")
    parser.add_argument('--git', action='store_true', help="Automatically enforce git sources")
    parser.add_argument('--local', action='store_true', help="Switch to local sources (development mode)")
    parser.add_argument('--toggle', action='store_true', help="Toggle between git and local sources based on current state")
    args = parser.parse_args()

    if args.toggle and (args.local or args.git):
        print("Error: --toggle cannot be used with --local or --git.")
        sys.exit(1)

    # Read the file for text editing
    try:
        with open('pyproject.toml', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    # Get all source packages from the lines (commented or uncommented)
    active_deps = set()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            uncommented = stripped[1:].strip()
        else:
            uncommented = stripped
        if ' = {' in uncommented:
            pkg = uncommented.split(' = {')[0].strip()
            if pkg:
                active_deps.add(pkg)

    # Determine mode
    if args.toggle:
        # Check if any source has uncommented local
        has_local = False
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('#'):
                for pkg in active_deps:
                    if stripped.startswith(pkg + ' = {') and 'path =' in stripped:
                        has_local = True
                        break
                if has_local:
                    break
        if has_local:
            mode = 'git'
        else:
            mode = 'local'
        print(f"Toggling to {mode} mode.")
    elif args.local:
        mode = 'local'
    else:
        mode = 'git'

    modified = False
    if mode == 'local':
        # Switch to local: comment git lines, uncomment local lines for all sources
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                uncommented = stripped[1:].strip()
            else:
                uncommented = stripped
            for pkg in active_deps:
                if uncommented.startswith(pkg + ' = {') and 'git =' in uncommented:
                    if not stripped.startswith('#'):
                        lines[i] = '#' + line
                        modified = True
                        break
                elif uncommented.startswith(pkg + ' = {') and 'path =' in uncommented:
                    if stripped.startswith('#'):
                        lines[i] = line[1:]
                        modified = True
                        break
    else:  # git
        # Comment local lines, uncomment git lines for all sources
        bad_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith('#'):
                for pkg in active_deps:
                    if stripped.startswith(pkg + ' = {') and ('path =' in stripped or 'editable = true' in stripped):
                        bad_lines.append(i)
                        break
        if bad_lines:
            for i in sorted(bad_lines, reverse=True):
                lines[i] = '#' + lines[i]
            modified = True
        # Now uncomment git lines
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                uncommented = stripped[1:].strip()
                for pkg in active_deps:
                    if uncommented.startswith(pkg + ' = {') and 'git =' in uncommented:
                        lines[i] = line[1:]
                        modified = True
                        break
        if bad_lines or modified:
            print("Switched to git mode.")
        elif not args.toggle:
            print("OK: Already in git mode.")

    if modified:
        with open('pyproject.toml', 'w') as f:
            f.writelines(lines)
        # Print the updated sources block
        print("Updated [tool.uv.sources]:")
        in_sources = False
        for line in lines:
            if line.strip() == '[tool.uv.sources]':
                in_sources = True
                print(line.rstrip())
            elif in_sources:
                if line.strip().startswith('[') and line.strip() != '[tool.uv.sources]':
                    break
                print(line.rstrip())
        print("pyproject.toml updated.")
    elif mode == 'git' and not args.git and not args.toggle:
        if bad_lines:
            print("Error: Found uncommented local sources.")
            for i in bad_lines:
                match = lines[i].strip().split(' = ')[0]
                print(f"  {match}")
            print("Run with --git to auto-fix.")
            sys.exit(1)
        else:
            print("OK: Already in git mode.")


if __name__ == '__main__':
    main()