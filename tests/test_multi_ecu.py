import pytest
from unittest.mock import patch, MagicMock
from udsonip.multi_ecu import DoIPMultiECUClient
from udsonip.exceptions import ECUNotFoundError, ConnectionError


@pytest.fixture
def manager():
    """Fixture for a DoIPMultiECUClient instance."""
    with patch("udsonip.multi_ecu.DoIPClient"):
        manager = DoIPMultiECUClient("192.168.1.1")
        yield manager
        manager.close()


class TestDoIPMultiECUClient:
    """Tests for the DoIPMultiECUClient."""

    def test_init(self):
        """Test that the client initializes correctly."""
        manager = DoIPMultiECUClient(
            "192.168.1.1", client_ip="192.168.1.100", client_logical_address=0x0E01
        )
        assert manager._gateway_ip == "192.168.1.1"
        assert manager._client_ip == "192.168.1.100"
        assert manager._client_logical_address == 0x0E01
        assert not manager._connected

    def test_add_and_list_ecus(self, manager):
        """Test adding and listing ECUs."""
        assert manager.list_ecus() == {}
        manager.add_ecu("engine", 0x00E0)
        manager.add_ecu("transmission", 0x00E1)
        assert manager.list_ecus() == {"engine": 0x00E0, "transmission": 0x00E1}

    def test_remove_ecu(self, manager):
        """Test removing an ECU."""
        manager.add_ecu("engine", 0x00E0)
        manager.add_ecu("transmission", 0x00E1)
        manager.remove_ecu("engine")
        assert manager.list_ecus() == {"transmission": 0x00E1}
        # Test removing a non-existent ECU
        manager.remove_ecu("non_existent")
        assert manager.list_ecus() == {"transmission": 0x00E1}

    def test_remove_ecu_with_cache(self, manager):
        """Test that removing an ECU also clears the cache."""
        manager.add_ecu("engine", 0x00E0)
        # Pre-populate cache
        manager._connections["engine"] = MagicMock()
        manager._clients["engine"] = MagicMock()

        manager.remove_ecu("engine")
        assert "engine" not in manager._connections
        assert "engine" not in manager._clients

    @patch("udsonip.multi_ecu.UDSClient")
    @patch("udsonip.multi_ecu.UdsOnIpConnection")
    def test_ecu_context_manager(self, MockUdsOnIpConnection, MockUDSClient, manager):
        """Test the ecu context manager."""
        manager.add_ecu("engine", 0x00E0)

        with manager.ecu("engine") as ecu:
            assert ecu == MockUDSClient.return_value
            MockUdsOnIpConnection.assert_called_once_with(manager._doip, 0x00E0)
            MockUDSClient.assert_called_once_with(MockUdsOnIpConnection.return_value)

    def test_ecu_not_found(self, manager):
        """Test that ECUNotFoundError is raised for non-existent ECU."""
        with pytest.raises(ECUNotFoundError):
            with manager.ecu("non_existent"):
                pass

    @patch("udsonip.multi_ecu.UDSClient")
    @patch("udsonip.multi_ecu.UdsOnIpConnection")
    def test_switch_to(self, MockUdsOnIpConnection, MockUDSClient, manager):
        """Test the switch_to method."""
        manager.add_ecu("engine", 0x00E0)
        client = manager.switch_to("engine")
        assert client == MockUDSClient.return_value

    @patch("udsonip.multi_ecu.UDSClient")
    @patch("udsonip.multi_ecu.UdsOnIpConnection")
    def test_close(self, MockUdsOnIpConnection, MockUDSClient, manager):
        """Test that the close method cleans up resources."""
        manager.add_ecu("engine", 0x00E0)
        # Prime the connection
        with manager.ecu("engine"):
            pass

        # Get the mocked connection to check if close is called
        mock_connection = manager._connections["engine"]

        manager.close()

        mock_connection.close.assert_called_once()
        manager._doip.close.assert_called_once()
        assert not manager._connected
        assert not manager._connections
        assert not manager._clients

    @patch("udsonip.multi_ecu.DoIPMultiECUClient._ensure_connected")
    def test_ensure_connected_failure(self, mock_ensure_connected):
        """Test that a ConnectionError is raised if the DoIPClient fails to connect."""
        mock_ensure_connected.side_effect = ConnectionError("Connection failed")
        manager = DoIPMultiECUClient("192.168.1.1")
        manager.add_ecu("engine", 0x00E0)

        with pytest.raises(ConnectionError, match="Connection failed"):
            with manager.ecu("engine"):
                pass

    @patch("udsonip.multi_ecu.DoIPClient")
    def test_manager_as_context_manager(self, MockDoIPClient):
        """Test using the manager as a context manager."""
        with DoIPMultiECUClient("192.168.1.1") as manager:
            manager.add_ecu("engine", 0x00E0)
            with manager.ecu("engine"):
                pass

        # Check that close was called on exit

    @patch("udsonip.multi_ecu.UDSClient")
    @patch("udsonip.multi_ecu.UdsOnIpConnection")
    def test_get_client_cache(self, MockUdsOnIpConnection, MockUDSClient, manager):
        """Test that the client is cached and reused."""
        manager.add_ecu("engine", 0x00E0)

        # First call, should create a new client
        client1 = manager._get_client("engine")
        assert client1 == MockUDSClient.return_value
        MockUDSClient.assert_called_once()

        # Second call, should return the cached client
        client2 = manager._get_client("engine")
        assert client2 == client1
        MockUDSClient.assert_called_once()  # Should still be called only once

    def test_ecu_context_exception(self, manager):
        """Test that exceptions are re-raised with context from the ecu context manager."""
        manager.add_ecu("engine", 0x00E0)

        with pytest.raises(
            ValueError, match="Error communicating with ECU 'engine': Test exception"
        ):
            with manager.ecu("engine"):
                raise ValueError("Test exception")

    @patch("udsonip.multi_ecu.UdsOnIpConnection")
    def test_close_with_connection_error(self, MockUdsOnIpConnection, manager):
        """Test that close continues even if a connection fails to close."""
        manager.add_ecu("engine", 0x00E0)
        with manager.ecu("engine"):
            pass
        manager._connections["engine"].close.side_effect = Exception("Close failed")

        manager.close()
        manager._doip.close.assert_called_once()

    def test_close_with_disconnect_error(self, manager):
        """Test that close continues even if the DoIP client fails to disconnect."""
        manager.add_ecu("engine", 0x00E0)
        with manager.ecu("engine"):
            pass
        manager._doip.close.side_effect = Exception("Disconnect failed")

        manager.close()
        assert not manager._connected

        manager._doip.close.assert_called_once()
