import unittest
from unittest.mock import MagicMock, patch
from libs.gatherer.linux_os_gatherer import LinuxOSGatherer


class TestLinuxOSGatherer(unittest.TestCase):
    def setUp(self):
        self.gatherer = LinuxOSGatherer(
            host='test.example.com',
            user='testuser',
            password='testpass'
        )
        self.gatherer.runner = MagicMock()

    def test_get_hostname_normal(self):
        """通常のホスト名を取得するテスト"""
        expected_hostname = 'test-server.example.com'
        self.gatherer.runner.exec.return_value = expected_hostname

        result = self.gatherer.get_hostname()

        self.assertEqual(result, expected_hostname)
        self.gatherer.runner.exec.assert_called_once_with('hostname')

    def test_get_hostname_with_spaces(self):
        """ホスト名にスペースが含まれる場合のテスト"""
        expected_hostname = 'test server.example.com'
        self.gatherer.runner.exec.return_value = expected_hostname

        result = self.gatherer.get_hostname()

        self.assertEqual(result, expected_hostname)
        self.gatherer.runner.exec.assert_called_once_with('hostname')

    def test_get_hostname_with_special_chars(self):
        """ホスト名に特殊文字が含まれる場合のテスト"""
        expected_hostname = 'test-server-01.example.com'
        self.gatherer.runner.exec.return_value = expected_hostname

        result = self.gatherer.get_hostname()

        self.assertEqual(result, expected_hostname)
        self.gatherer.runner.exec.assert_called_once_with('hostname')

    def test_get_hostname_cached(self):
        """キャッシュされたホスト名を返すテスト"""
        expected_hostname = 'test-server.example.com'
        self.gatherer.hostname = expected_hostname

        result = self.gatherer.get_hostname()

        self.assertEqual(result, expected_hostname)
        self.gatherer.runner.exec.assert_not_called()

    def test_get_hostname_empty(self):
        """空のホスト名が返される場合のテスト"""
        expected_hostname = ''
        self.gatherer.runner.exec.return_value = expected_hostname

        result = self.gatherer.get_hostname()

        self.assertEqual(result, expected_hostname)
        self.gatherer.runner.exec.assert_called_once_with('hostname')


if __name__ == '__main__':
    unittest.main()
