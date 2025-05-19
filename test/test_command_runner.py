import unittest
import os
from libs.utils.command_runner import CommandRunner, OS2SheetCommandRunnerException


class TestCommandRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """テストクラスの前準備"""
        # 環境変数からテスト用サーバーの接続情報を取得
        cls.test_host = os.getenv('OS2SHEET_TEST_SSH_HOST', 'localhost')
        cls.test_user = os.getenv('OS2SHEET_TEST_SSH_USER', 'testuser')
        cls.test_password = os.getenv('OS2SHEET_TEST_SSH_PASSWORD', 'testpass')
        cls.test_port = int(os.getenv('OS2SHEET_TEST_SSH_PORT', '22'))
        cls.test_root_password = os.getenv(
            'OS2SHEET_TEST_SSH_ROOT_PASSWORD', 'rootpass')

    def setUp(self):
        """各テストの前準備"""
        self.runner = CommandRunner(
            host=self.test_host,
            user=self.test_user,
            password=self.test_password,
            port=self.test_port,
        )

    def tearDown(self):
        """各テストの後処理"""
        self.runner.close()

    def test_connect_success(self):
        """接続成功のテスト"""
        self.runner.connect()
        self.assertTrue(self.runner.is_connected)
        self.assertEqual(self.runner.status, 1)  # CMD_RUNNER_LOGIN

    def test_exec_command_success(self):
        """コマンド実行成功のテスト"""
        self.runner.connect()
        result = self.runner.exec("echo test")
        self.assertIn('test', result)

    def test_exec_command_with_special_chars(self):
        """特殊文字を含むコマンドのテスト"""
        self.runner.connect()
        result = self.runner.exec("echo 'test\nwith\nnewlines'")
        self.assertIn('test', result)
        self.assertIn('with', result)
        self.assertIn('newlines', result)

    def test_su_success(self):
        """suコマンド成功のテスト"""
        self.runner.connect()
        self.runner.su(self.test_root_password)
        self.assertEqual(self.runner.status, 2)  # CMD_RUNNER_ROOTLOGIN

    def test_exec_command_as_root(self):
        """rootユーザーでのコマンド実行テスト"""
        self.runner.connect()
        self.runner.su(self.test_root_password)
        result = self.runner.exec("whoami")
        self.assertIn('root', result)

    def test_context_manager(self):
        """コンテキストマネージャのテスト"""
        with CommandRunner(
            host=self.test_host,
            user=self.test_user,
            password=self.test_password,
            port=self.test_port,
            prompt_pattern=r'\[.+\][\$,#] $'  # プロンプトパターンを明示的に指定
        ) as runner:
            self.assertTrue(runner.is_connected)
            self.assertEqual(runner.status, 1)  # CMD_RUNNER_LOGIN
            result = runner.exec("echo test")
            self.assertIn('test', result)

        # コンテキストを抜けた後は接続が閉じられていることを確認
        self.assertFalse(runner.is_connected)
        self.assertEqual(runner.status, 0)  # CMD_RUNNER_UNLOGIN

    def test_exec_command_timeout(self):
        """コマンド実行タイムアウトのテスト"""
        self.runner.connect()
        with self.assertRaises(OS2SheetCommandRunnerException) as cm:
            self.runner.exec("sleep 2", timeout=1)
        self.assertIn("Timeout", str(cm.exception))

    def test_invalid_credentials(self):
        """不正な認証情報のテスト"""
        runner = CommandRunner(
            host=self.test_host,
            user=self.test_user,
            password="wrong_password",
            port=self.test_port
        )
        with self.assertRaises(OS2SheetCommandRunnerException):
            runner.connect()

    def test_invalid_host(self):
        """不正なホストのテスト"""
        runner = CommandRunner(
            host="invalid_host",
            user=self.test_user,
            password=self.test_password,
            port=self.test_port
        )
        with self.assertRaises(OS2SheetCommandRunnerException):
            runner.connect()


if __name__ == '__main__':
    unittest.main()
