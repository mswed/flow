import unittest
from unittest.mock import patch, MagicMock

from flow import Flow


class TestFlow(unittest.TestCase):
    @patch("sgtk.platform.current_engine")
    def test_get_engine(self, mock_current_engine):
        # Setup mock engine
        mock_engine = MagicMock()
        mock_engine.shotgun = "mock_shotgun"
        mock_engine.sgtk = "mock_sgtk"
        mock_engine.get_metrics_properties.return_value = {"app": "test"}
        mock_current_engine.return_value = mock_engine

        # Test
        flow = Flow()
        flow.get_engine()

        # Assertions
        self.assertEqual(flow.api, "mock_shotgun")
        self.assertEqual(flow.tk, "mock_sgtk")
        self.assertEqual(flow.engine_info, {"app": "test"})

    @patch("sgtk.platform.current_engine")
    @patch("sgtk.authentication.ShotgunAuthenticator")
    def test_connect_user(self, mock_authenticator, mock_current_engine):
        # Setup mocks
        mock_current_engine.return_value = None
        mock_auth = MagicMock()
        mock_user = MagicMock()
        mock_connection = MagicMock()
        mock_user.create_sg_connection.return_value = mock_connection
        mock_auth.get_user.return_value = mock_user
        mock_authenticator.return_value = mock_auth

        # Test
        flow = Flow.connect(user=True)

        # Assertions
        self.assertEqual(flow.api, mock_connection)
        mock_auth.get_user.assert_called_once()

    @patch("sgtk.platform.current_engine")
    @patch("sgtk.authentication.ShotgunAuthenticator")
    @patch("os.environ.get")
    def test_connect_script(
        self, mock_env_get, mock_authenticator, mock_current_engine
    ):
        # Setup mocks
        mock_current_engine.return_value = None
        mock_env_get.return_value = "script_key_value"
        mock_auth = MagicMock()
        mock_script_user = MagicMock()
        mock_connection = MagicMock()
        mock_script_user.create_sg_connection.return_value = mock_connection
        mock_auth.create_script_user.return_value = mock_script_user
        mock_authenticator.return_value = mock_auth

        # Test
        flow = Flow.connect(script_key="nuke")

        # Assertions
        mock_auth.create_script_user.assert_called_once_with(
            api_script="SCRIPT_KEY_NUKE", api_key="script_key_value"
        )


if __name__ == "__main__":
    unittest.main()
