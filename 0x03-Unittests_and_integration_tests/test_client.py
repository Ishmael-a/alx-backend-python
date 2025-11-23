#!/usr/bin/env python3
"""Unit tests for client module."""
import unittest
from parameterized import parameterized, parameterized_class
from typing import Dict
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns correct value."""
        test_payload = {"login": org_name, "id": 123}
        mock_get_json.return_value = test_payload
        
        client = GithubOrgClient(org_name)
        result = client.org
        
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns expected value."""
        known_payload = {
            "login": "google",
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        
        with patch.object(GithubOrgClient,'org',new_callable=PropertyMock,return_value=known_payload):
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test that public_repos returns expected list of repos."""
        mock_repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_repos_payload
        
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/google/repos"
        ) as mock_public_repos_url:
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()


    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(
        self,
        repo: Dict,
        license_key: str,
        expected: bool
    ) -> None:
        """Test that has_license returns correct boolean value."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class fixtures before running tests."""
        def get_side_effect(url): 
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload.get("repos_url"):
                print("Fetching repos payload in side effect...", cls.repos_payload)
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response
        
        cls.get_patcher = patch('requests.get', side_effect = get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down class fixtures after running tests."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test public_repos method in integration."""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test public_repos method with license filter."""
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()