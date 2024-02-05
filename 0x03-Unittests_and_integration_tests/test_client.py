#!/usr/bin/env python3
"""Module for testing the GithubOrgClient class."""
import unittest
from typing import Dict
from unittest.mock import MagicMock, Mock, PropertyMock, patch
from parameterized import parameterized, parameterized_class
from requests import HTTPError

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient."""

    @parameterized.expand([
        ("google", {'login': "google"}),
        ("abc", {'login': "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org: str, expected: Dict,
                 mocked_get_json: MagicMock) -> None:
        """Test the org method of GithubOrgClient.

        Args:
            org (str): Organization name.
            expected (Dict): Expected API response.
            mocked_get_json (MagicMock): Mocked get_json function.
        """
        mocked_get_json.return_value = MagicMock(return_value=expected)
        client = GithubOrgClient(org)
        self.assertEqual(client.org(), expected)
        mocked_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org}")

    def test_public_repos_url(self) -> None:
        """Test the public_repos_url property of GithubOrgClient."""
        with patch("client.GithubOrgClient.org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {
                'repos_url': "https://api.github.com/users/google/repos"}
            self.assertEqual(
                GithubOrgClient("google").public_repos_url,
                "https://api.github.com/users/google/repos",
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """Test the public_repos method of GithubOrgClient.

        Args:
            mock_get_json (MagicMock): Mocked get_json function.
        """
        payload = [
            {
                "id": 7697149,
                "name": "episodes.dart",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/episodes.dart",
                "created_at": "2013-01-19T00:31:37Z",
                "updated_at": "2019-09-23T11:53:58Z",
                "has_issues": True,
                "forks": 22,
                "default_branch": "master",
            },
            {
                "id": 8566972,
                "name": "kratu",
                "private": False,
                "owner": {"login": "google", "id": 1342004},
                "fork": False,
                "url": "https://api.github.com/repos/google/kratu",
                "created_at": "2013-03-04T22:52:33Z",
                "updated_at": "2019-11-15T22:22:16Z",
                "has_issues": True,
                "forks": 32,
                "default_branch": "master",
            },
        ]
        mock_get_json.return_value = payload
        with patch("client.GithubOrgClient.public_repos_url", new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/users/google/repos"
            self.assertEqual(
                GithubOrgClient("google").public_repos(),
                ["episodes.dart", "kratu"],
            )
            mock_repos_url.assert_called_once()
        mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "bsd-3-clause"}}, "bsd-3-clause", True),
        ({"license": {"key": "bsl-1.0"}}, "bsd-3-clause", False),
    ])
    def test_has_license(self, repo: Dict, key: str, expected: bool) -> None:
        """Test the has_license method of GithubOrgClient.

        Args:
            repo (Dict): Repository dictionary.
            key (str): License key to check.
            expected (bool): Expected result of has_license method.
        """
        client = GithubOrgClient("google")
        has_license = client.has_license(repo, key)
        self.assertEqual(has_license, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test class."""
        cls.get_patcher = patch('requests.get')
        cls.get_mock = cls.get_patcher.start()

        cls.get_mock.side_effect = [
            Mock(json=Mock(return_value=cls.org_payload)),
            Mock(json=Mock(return_value=cls.repos_payload)),
        ]

        cls.client = GithubOrgClient("google")

    def test_public_repos(self) -> None:
        """Test the public_repos method of GithubOrgClient."""
        self.assertEqual(self.client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test the public_repos method of GithubOrgClient with a specific license."""
        self.assertEqual(
            self.client.public_repos(
                license="apache-2.0"),
            self.apache2_repos)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the test class."""
        cls.get_patcher.stop()


if __name__ == "__main__":
    unittest.main()
