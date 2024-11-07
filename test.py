import configparser
import io
import unittest
from unittest.mock import patch, mock_open
from main import get_package_dependencies, extract_package_name, print_dependencies, main


class TestVisualizer(unittest.TestCase):
    @patch("requests.get")
    def test_get_package_dependencies_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'info': {'requires_dist': ['package2', 'package3']}}
        dependencies = get_package_dependencies("package1")
        self.assertEqual(dependencies, ['package2', 'package3'])
        mock_get.assert_called_once_with('https://pypi.org/pypi/package1/json')

    @patch("requests.get")
    def test_get_package_dependencies_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        dependencies = get_package_dependencies("package1")
        self.assertEqual(dependencies, [])
        mock_get.assert_called_once_with('https://pypi.org/pypi/package1/json')

    @patch("requests.get")
    def test_get_package_dependencies_no_requires_dist(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'info': {}}
        dependencies = get_package_dependencies("package1")
        self.assertEqual(dependencies, [])
        mock_get.assert_called_once_with('https://pypi.org/pypi/package1/json')

    def test_extract_package_name(self):
        self.assertEqual(extract_package_name("package2>=1.0.0"), "package2")
        self.assertEqual(extract_package_name("package3[extra]"), "package3")
        self.assertEqual(extract_package_name("package4 ; extra"), "package4")

    @patch("builtins.open", new_callable=mock_open)
    def test_print_dependencies_empty(self, mock_file):
        print_dependencies("package1", [], 1, output_file="test.txt")
        mock_file.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_print_dependencies_with_output_file(self, mock_file):
        print_dependencies("package1", ["package2"], 1, output_file="test.txt")
        mock_file.assert_called_once_with("test.txt", "a")
        mock_file.return_value.write.assert_called_once_with("- package1\n")

    def test_print_dependencies_no_output_file(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_dependencies("package1", ["package2"], 1)
            self.assertEqual(mock_stdout.getvalue(), "- package1\n")

    @patch("os.remove")
    @patch("builtins.open", new_callable=mock_open)
    @patch("configparser.ConfigParser.read", return_value=None)
    def test_main(self, mock_read, mock_file, mock_remove):
        mock_config = configparser.ConfigParser()
        mock_config.get = lambda section, option: {
            'settings': {
                'package_name': 'package1',
                'max_depth': '1',
                'output_file': 'test.txt'
            }
        }[section][option]
        mock_config.getint = lambda section, option: {
            'settings': {
                'package_name': 'package1',
                'max_depth': '1',
                'output_file': 'test.txt'
            }
        }[section][option]

        with patch('your_module.configparser.ConfigParser', return_value=mock_config):
            main("config.ini")

        mock_file.assert_called_once_with('test.txt', 'a')
        mock_remove.assert_called_once_with('test.txt')
        mock_file().write.assert_called_once_with("- package1\n")


if __name__ == "__main__":
    unittest.main()