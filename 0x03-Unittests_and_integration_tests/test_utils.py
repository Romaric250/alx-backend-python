#!/usr/bin/env python3
"""Unit tests for utility functions."""

import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map function.

        Args:
            nested_map (dict): Nested dictionary.
            path (tuple): Path to access the value.
            expected: Expected output.
        """
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError)
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected):
        """Test access_nested_map function for exceptions.

        Args:
            nested_map (dict): Nested dictionary.
            path (tuple): Path to access the value.
            expected: Expected exception.
        """
        with self.assertRaises(expected):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Test class for get_json function."""

    @parameterized.expand([
        ('http://example.com', {'payload': True}),
        ('http://holberton.io', {'payload': False})
    ])
    def test_get_json(self, url, expected):
        """Test get_json function.

        Args:
            url (str): URL to fetch JSON from.
            expected: Expected JSON response.
        """
        mock_response = Mock()
        mock_response.json.return_value = expected
        with patch('requests.get', return_value=mock_response):
            response = get_json(url)
            self.assertEqual(response, expected)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator."""

    def test_memoize(self):
        """Test memoize decorator.

        Returns:
            Type: Description
        """
        class TestClass:
            """Test class."""

            def a_method(self):
                """Test method.

                Returns:
                    Type: Description
                """
                return 42

            @memoize
            def a_property(self):
                """Test property.

                Returns:
                    Type: Description
                """
                return self.a_method()

        test_obj = TestClass()
        with patch.object(test_obj, 'a_method') as mock_method:
            mock_method.return_value = 42
            result1 = test_obj.a_property
            result2 = test_obj.a_property
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
