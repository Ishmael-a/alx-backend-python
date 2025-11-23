
# !/usr/bin/env python3
"""Unit tests for utils module."""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from typing import Dict, Tuple, Any
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict,
        path: Tuple,
        expected: Any
    ) -> None:
        """Test that access_nested_map returns expected results."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict,
        path: Tuple
    ) -> None:
        """Test that KeyError is raised for invalid paths."""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Test cases for get_json function."""
    @parameterized.expand([
      ("http://example.com", {"payload": True}),  
      ("http://holberton.io", {"payload": False})  
    ])
    @patch('utils.requests.get')
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict,
        mock_get: Mock
    ) -> None:
        """Test that get_json returns expected result."""
        # construct response object
        response_obj = Mock()
        response_obj.json.return_value = test_payload
        mock_get.return_value = response_obj

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)

        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator."""

    def test_memoize(self) -> None:
        """Test that memoize decorator caches results correctly."""
        class TestClass:
            """Test class for memoization."""

            def a_method(self):
                """Method that returns a value."""
                return 42

            @memoize
            def a_property(self):
                """Property that calls a_method."""
                return self.a_method()
            
        with patch.object(TestClass,'a_method', return_value = 42) as mock_method:
            test_obj = TestClass()
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            # first assert that 42 is returned on both occassions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # assert that the a_method is called only once
            mock_method.assert_called_once()


if __name__=='__main__':
    unittest.main()