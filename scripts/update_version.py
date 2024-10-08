import re
import os


def update_version(file_path, version_pattern, new_version):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    updated_content = re.sub(version_pattern, new_version, content)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    init_file = os.path.join(root_dir, "repocoder", "__init__.py")
    setup_file = os.path.join(root_dir, "setup.py")

    # Read current version
    with open(init_file, "r", encoding="utf-8") as file:
        init_content = file.read()
    current_version_match = re.search(
        r'__version__\s*=\s*["\']([^"\']+)["\']', init_content
    )
    if not current_version_match:
        raise ValueError("Version not found in __init__.py")
    current_version = current_version_match.group(1)

    # Increment patch version
    version_parts = current_version.split(".")
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = ".".join(version_parts)

    # Update __init__.py
    update_version(
        init_file,
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
    )

    # Update setup.py
    update_version(
        setup_file, r'version\s*=\s*["\']([^"\']+)["\']', f'version="{new_version}"'
    )

    print(f"Updated version from {current_version} to {new_version}")


if __name__ == "__main__":
    main()
