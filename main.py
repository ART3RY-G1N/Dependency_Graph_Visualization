import configparser
import importlib.metadata
import sys


def get_dependencies(package_name, depth, current_depth=0, visited=None):
    if visited is None:
        visited = set()

    if depth == 0 or current_depth > depth or package_name in visited:
        return []

    visited.add(package_name)
    dependencies = []

    try:
        # Получаем метаданные пакета
        pkg = importlib.metadata.metadata(package_name)
        # Получаем список зависимостей
        requires = pkg.get_all('Requires-Dist')

        for req in requires:
            dep_name = req.split(';')[0].strip()  # Убираем маркеры окружения
            dependencies.append(dep_name)
            dependencies.extend(get_dependencies(dep_name, depth, current_depth + 1, visited))
    except Exception as e:
        print(f"Package {package_name} не найден: {e}")

    return dependencies


def generate_graph(dependencies):
    graph = 'digraph G {\n'
    for dep in dependencies:
        graph += f'    "{dep}";\n'
    graph += '}'
    return graph


def main(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    package_name = config.get('settings', 'package_name')
    max_depth = config.getint('settings', 'max_depth')
    output_file = config.get('settings', 'output_file')

    dependencies = get_dependencies(package_name, max_depth)
    graph_code = generate_graph(dependencies)

    with open(output_file, 'w') as f:
        f.write(graph_code)

    print(graph_code)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python main.py <config_file>")
        sys.exit(1)

    main(sys.argv[1])