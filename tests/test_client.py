import pytest
from unittest.mock import patch, MagicMock
from udsonip.client import UdsOnIpClient
from udsonip.exceptions import ConnectionError, AddressSwitchError


@pytest.fixture
def client():
    """Fixture for a UdsOnIpClient instance."""
    with patch("udsonip.client.DoIPClient"), patch("udsonip.client.UDSClient"), patch(
        "udsonip.client.UdsOnIpConnection"
    ):
        client = UdsOnIpClient("192.168.1.1", 0x00E0)
        yield client
        client.close()


class TestUdsOnIpClient:
    """Tests for the UdsOnIpClient."""

    @patch("udsonip.client.DoIPClient")
    @patch("udsonip.client.UDSClient")
    @patch("udsonip.client.UdsOnIpConnection")
    def test_init(self, MockUdsOnIpConnection, MockUDSClient, MockDoIPClient):
        """Test that the client initializes correctly."""
        UdsOnIpClient(
            "192.168.1.1", 0x00E0, client_ip="192.168.1.100", client_logical_address=0x0E01
        )

        MockDoIPClient.assert_called_once_with(
            ecu_ip_address="192.168.1.1",
            ecu_logical_address=0x00E0,
            tcp_port=13400,
            udp_port=13400,
            client_ip_address="192.168.1.100",
            client_logical_address=0x0E01,
            activation_type=0,
            protocol_version=0x03,
        )
        MockUdsOnIpConnection.assert_called_once_with(MockDoIPClient.return_value, 0x00E0)
        MockUDSClient.assert_called_once_with(MockUdsOnIpConnection.return_value)

        MockDoIPClient.return_value.connect.assert_called_once()
        MockUdsOnIpConnection.return_value.open.assert_called_once()

    @patch("udsonip.client.DoIPClient")
    @patch("udsonip.client.UDSClient")
    @patch("udsonip.client.UdsOnIpConnection")
    def test_init_connection_error(self, MockUdsOnIpConnection, MockUDSClient, MockDoIPClient):
        """Test that a ConnectionError is raised if the DoIPClient fails to connect."""
        MockDoIPClient.return_value.connect.side_effect = Exception("Connection failed")

        with pytest.raises(
            ConnectionError, match="Failed to connect to 192.168.1.1:0xe0: Connection failed"
        ):
            UdsOnIpClient("192.168.1.1", 0x00E0)

    def test_target_address_setter(self, client):
        """Test setting the target address."""
        client.target_address = 0x00E1
        assert client._connection.target_address == 0x00E1

    @patch("udsonip.client.DoIPClient")
    @patch("udsonip.client.UDSClient")
    def test_target_address_setter_error(self, MockUDSClient, MockDoIPClient):
        """Test that an AddressSwitchError is raised for an invalid address."""
        client = UdsOnIpClient("192.168.1.1", 0x00E0)
        with pytest.raises(
            AddressSwitchError,
            match="Invalid logical address: 0x10000. Must be a 16-bit integer.",
        ):
            client.target_address = 0x10000

    def test_uds_property(self, client):
        """Test that the uds property returns the underlying UDSClient."""
        assert isinstance(client.uds, MagicMock)  # In the test fixture, UDSClient is a MagicMock

    def test_close(self, client):
        """Test that the close method closes the connection."""
        client.close()
        client._connection.close.assert_called_once()
        client._doip.disconnect.assert_called_once()

    @patch("udsonip.client.UdsOnIpConnection")
    def test_close_error(self, MockUdsOnIpConnection):
        """Test that a ConnectionError is raised if closing the connection fails."""
        with patch("udsonip.client.DoIPClient"), patch("udsonip.client.UDSClient"):
            client = UdsOnIpClient("192.168.1.1", 0x00E0)
        client._connection.close.side_effect = Exception("Close failed")
        with pytest.raises(ConnectionError, match="Error closing connection: Close failed"):
            client.close()

    def test_context_manager(self):
        """Test that the client can be used as a context manager."""
        with patch("udsonip.client.DoIPClient"), patch("udsonip.client.UDSClient"), patch(
            "udsonip.client.UdsOnIpConnection"
        ):
            with UdsOnIpClient("192.168.1.1", 0x00E0) as client:
                assert isinstance(client, UdsOnIpClient)
            # close() is called on exit, so disconnect() should have been called
            client._doip.disconnect.assert_called_once()


class TestConvenienceMethods:
    """Tests for the convenience methods."""

    def test_tester_present(self, client):
        """Test the tester_present method."""
        with patch.object(client, "_uds") as mock_uds:
            client.tester_present(suppress_response=True)
            mock_uds.tester_present.assert_called_once_with(suppress_response=True)

    def test_read_data_by_identifier(self, client):
        """Test the read_data_by_identifier method."""
        with patch.object(client, "_uds") as mock_uds:
            client.read_data_by_identifier(0xF190)
            mock_uds.read_data_by_identifier.assert_called_once_with(0xF190)

    def test_write_data_by_identifier(self, client):
        """Test the write_data_by_identifier method."""
        with patch.object(client, "_uds") as mock_uds:
            client.write_data_by_identifier(0xF190, b"\x01\x02")
            mock_uds.write_data_by_identifier.assert_called_once_with(0xF190, b"\x01\x02")

    def test_read_dtc_information(self, client):
        """Test the read_dtc_information method."""
        with patch.object(client, "_uds") as mock_uds:
            from udsoncan import services

            client.read_dtc_information(dtc_status_mask=0x2F)
            mock_uds.read_dtc_information.assert_called_once_with(
                services.ReadDTCInformation.Subfunction.reportDTCByStatusMask, 0x2F
            )

    def test_clear_dtc(self, client):
        """Test the clear_dtc method."""
        with patch.object(client, "_uds") as mock_uds:
            client.clear_dtc(0x123456)
            mock_uds.clear_dtc.assert_called_once_with(0x123456)

    def test_ecu_reset(self, client):
        """Test the ecu_reset method."""
        with patch.object(client, "_uds") as mock_uds:
            client.ecu_reset(2)
            mock_uds.ecu_reset.assert_called_once_with(2)

    def test_change_session(self, client):
        """Test the change_session method."""
        with patch.object(client, "_uds") as mock_uds:
            client.change_session(3)
            mock_uds.change_session.assert_called_once_with(3)

    def test_security_access_seed(self, client):
        """Test the security_access method for requesting a seed."""
        with patch.object(client, "_uds") as mock_uds:
            client.security_access(1)
            mock_uds.request_seed.assert_called_once_with(1)

    def test_security_access_key(self, client):
        """Test the security_access method for sending a key."""
        with patch.object(client, "_uds") as mock_uds:
            client.security_access(1, key=b"\x01\x02")
            mock_uds.send_key.assert_called_once_with(1, b"\x01\x02")

    def test_routine_control_start(self, client):
        """Test the routine_control method for starting a routine."""
        with patch.object(client, "_uds") as mock_uds:
            client.routine_control(0x1234, 1, data=b"\xab")
            mock_uds.start_routine.assert_called_once_with(0x1234, b"\xab")

    def test_routine_control_stop(self, client):
        """Test the routine_control method for stopping a routine."""
        with patch.object(client, "_uds") as mock_uds:
            client.routine_control(0x1234, 2, data=b"\xcd")
            mock_uds.stop_routine.assert_called_once_with(0x1234, b"\xcd")

    def test_routine_control_result(self, client):
        """Test the routine_control method for requesting results."""
        with patch.object(client, "_uds") as mock_uds:
            client.routine_control(0x1234, 3, data=b"\xef")
            mock_uds.get_routine_result.assert_called_once_with(0x1234, b"\xef")
