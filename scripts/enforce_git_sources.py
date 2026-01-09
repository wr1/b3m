import argparse
import re
import sys
import tomllib


def main():
    """Manage sources in pyproject.toml: enforce Git for production or switch to local for development."""
    parser = argparse.ArgumentParser(description="Check or fix sources in pyproject.toml for active dependencies")
    parser.add_argument('--fix', action='store_true', help="Automatically fix sources (comment local for --git, switch to local for --local)")
    parser.add_argument('--local', action='store_true', help="Switch to local sources for active dependencies (development mode)")
    args = parser.parse_args()

    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        print("Error: pyproject.toml not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing pyproject.toml: {e}")
        sys.exit(1)

    # Get active dependencies (uncommented in project.dependencies)
    active_deps = set()
    if 'project' in data and 'dependencies' in data['project']:
        for dep in data['project']['dependencies']:
            # Assuming deps are strings like "package" or "package>=1.0"
            # Extract package name (before any version spec)
            match = re.match(r'^([a-zA-Z0-9_-]+)', dep.strip())
            if match:
                active_deps.add(match.group(1))

    # Also check optional-dependencies if they exist (though typically dev tools)
    if 'project' in data and 'optional-dependencies' in data['project']:
        for group, deps in data['project']['optional-dependencies'].items():
            for dep in deps:
                match = re.match(r'^([a-zA-Z0-9_-]+)', dep.strip())
                if match:
                    active_deps.add(match.group(1))

    # Read the file for text editing
    try:
        with open('pyproject.toml', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    modified = False
    if args.local:
        # Switch to local: comment git lines, uncomment local lines for active deps
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                uncommented = stripped[1:].strip()
            else:
                uncommented = stripped
            for pkg in active_deps:
                # Check for git source
                if re.search(r'^' + re.escape(pkg) + r'\s*=\s*\{.*\bgit\s*=', uncommented):
                    if not stripped.startswith('#'):
                        lines[i] = '#' + line
                        modified = True
                        print(f"Commented git source for {pkg}")
                        break
                # Check for local source
                elif re.search(r'^' + re.escape(pkg) + r'\s*=\s*\{.*\bpath\s*=', uncommented):
                    if stripped.startswith('#'):
                        lines[i] = line[1:]  # Uncomment
                        modified = True
                        print(f"Uncommented local source for {pkg}")
                        break
    else:
        # Enforce git: comment local lines for active deps
        bad_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith('#'):
                for pkg in active_deps:
                    if re.search(r'^' + re.escape(pkg) + r'\s*=\s*\{.*(?:\bpath\s*=|\beditable\s*=\s*true)', stripped):
                        bad_lines.append(i)
                        break
        if bad_lines:
            if args.fix:
                # Comment out the bad lines
                for i in sorted(bad_lines, reverse=True):
                    lines[i] = '#' + lines[i]
                modified = True
                print(f"Fixed: Commented out local sources for active dependencies.")
            else:
                print("Error: Found uncommented local sources for active dependencies in pyproject.toml.")
                print("Active dependencies with local sources:")
                for i in bad_lines:
                    match = re.search(r'^([a-zA-Z0-9_-]+)\s*=', lines[i].strip())
                    if match:
                        print(f"  {match.group(1)}")
                print("Please comment them out for production commits, or run with --fix to auto-fix.")
                sys.exit(1)
        else:
            print("OK: No local sources found for active dependencies in pyproject.toml.")

    if modified:
        with open('pyproject.toml', 'w') as f:
            f.writelines(lines)
        print("pyproject.toml updated.")


if __name__ == '__main__':
    main()