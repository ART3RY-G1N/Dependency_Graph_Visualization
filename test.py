import unittest
from main import get_dependencies, generate_graph


class TestDependencyVisualizer(unittest.TestCase):
    def test_get_dependencies(self):
        dependencies = get_dependencies('pipdeptree', 1)
        self.assertIsInstance(dependencies, list)

    def test_generate_graph(self):
        dependencies = ['dep1', 'dep2']
        graph_code = generate_graph(dependencies)
        self.assertIn('digraph G {', graph_code)
        self.assertIn('"dep1";', graph_code)
        self.assertIn('"dep2";', graph_code)

if __name__ == '__main__':
    unittest.main()