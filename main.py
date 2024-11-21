import configparser
import requests
import sys
import re
import os


def get_package_dependencies(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            dependencies = data.get('info', {}).get('requires_dist', [])
            return dependencies if dependencies is not None else []
        else:
            return []
    except requests.RequestException as e:
        return []


def print_dependencies(package_name, dependencies, max_depth, depth=0, output_file=None):
    if depth == max_depth:
        return

    indent = "  " * depth
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{indent}- {package_name}\n")
    print(f"{indent}- {package_name}")

    if not dependencies:
        return

    for dependency in dependencies:
        dep_name = extract_package_name(dependency)
        print_dependencies(dep_name, get_package_dependencies(dep_name), max_depth, depth + 1, output_file)


def extract_package_name(dep_string):
    dep_string = re.sub(r'\[.*?\]', '', dep_string)
    return re.split('[ ;<>=]', dep_string)[0].strip()


def main(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    package_name = config.get('settings', 'package_name')
    max_depth = config.getint('settings', 'max_depth')
    output_file = config.get('settings', 'output_file')
    print(f"Dependencies for package '{package_name}':")

    if os.path.exists(output_file):
        os.remove(output_file)

    dependencies = get_package_dependencies(package_name)
    print_dependencies(package_name, dependencies, max_depth, output_file=output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    main(sys.argv[1])
