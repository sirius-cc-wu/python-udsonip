import pytest
import warnings
import socket
from unittest.mock import patch, MagicMock
from doipclient.messages import VehicleIdentificationResponse
from udsonip.discovery import ECUInfo, get_entity, discover_ecus


class TestECUInfo:
    """Tests for ECUInfo dataclass."""

    def test_init(self):
        """Test ECUInfo initialization."""
        ecu = ECUInfo(
            ip="192.168.1.10",
            logical_address=0x00E0,
            eid=b"VIN12345678901234",
            gid=b"\x00\x01",
        )

        assert ecu.ip == "192.168.1.10"
        assert ecu.logical_address == 0x00E0
        assert ecu.eid == b"VIN12345678901234"
        assert ecu.gid == b"\x00\x01"

    def test_str(self):
        """Test string representation."""
        ecu = ECUInfo(ip="192.168.1.10", logical_address=0x00E0)
        assert str(ecu) == "ECU(192.168.1.10 @ 0x00E0)"

    def test_repr(self):
        """Test repr representation."""
        ecu = ECUInfo(ip="192.168.1.10", logical_address=0x00E0)
        assert repr(ecu) == "ECUInfo(ip='192.168.1.10', logical_address=0x00E0)"

    @patch("udsonip.discovery.UdsOnIpClient")
    def test_connect(self, MockUdsOnIpClient):
        """Test the connect method creates a client."""
        ecu = ECUInfo(ip="192.168.1.10", logical_address=0x00E0)
        client = ecu.connect(client_ip="192.168.1.11")

        MockUdsOnIpClient.assert_called_once_with(
            ecu_ip="192.168.1.10",
            ecu_address=0x00E0,
            client_ip="192.168.1.11",
            protocol_version=0x03,
        )
        assert client == MockUdsOnIpClient.return_value


@patch("udsonip.discovery.DoIPClient")
def test_get_entity_found(MockDoIPClient):
    """Test get_entity when an ECU is found."""
    # Mock the announcement message
    mock_announcement = VehicleIdentificationResponse(
        vin=b"TESTVIN123456789",
        logical_address=0x1001,
        eid=b"EID123",
        gid=b"GID123",
        further_action_required=0x00,
    )

    # Configure the mock DoIPClient
    MockDoIPClient.get_entity.return_value = (("192.168.1.1", 13400), mock_announcement)

    # Call the function
    ecu_info = get_entity(ip="192.168.1.1")

    # Assertions
    assert isinstance(ecu_info, ECUInfo)
    assert ecu_info.ip == "192.168.1.1"
    assert ecu_info.logical_address == 0x1001
    assert ecu_info.eid == b"EID123"
    assert ecu_info.gid == b"GID123"
    MockDoIPClient.get_entity.assert_called_once_with(
        ecu_ip_address="192.168.1.1", protocol_version=0x03
    )


@patch("udsonip.discovery.DoIPClient")
def test_get_entity_not_found(MockDoIPClient):
    """Test get_entity when no ECU is found (timeout)."""
    # Configure the mock to raise a TimeoutError
    MockDoIPClient.get_entity.side_effect = TimeoutError

    # Call the function
    ecu_info = get_entity(ip="192.168.1.2")

    # Assertions
    assert ecu_info is None
    MockDoIPClient.get_entity.assert_called_once_with(
        ecu_ip_address="192.168.1.2", protocol_version=0x03
    )


@patch("udsonip.discovery.Parser")
@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_found(MockDoIPClient, MockParser):
    """Test discover_ecus when a single ECU is found."""
    # Mock the announcement message
    mock_announcement = VehicleIdentificationResponse(
        vin=b"TESTVIN123456789",
        logical_address=0x1002,
        eid=b"EID456",
        gid=b"GID456",
        further_action_required=0x00,
    )

    # Create mock socket
    mock_sock = MagicMock()
    MockDoIPClient._create_udp_socket.return_value = mock_sock
    MockDoIPClient._pack_doip.return_value = b"packed_data"

    # Mock parser to return the announcement
    mock_parser_instance = MockParser.return_value
    mock_parser_instance.read_message.return_value = mock_announcement

    # Mock socket.recvfrom to return data once, then raise timeout
    call_count = {"count": 0}

    def mock_recvfrom(size):
        call_count["count"] += 1
        if call_count["count"] == 1:
            return (b"response_data", ("192.168.1.3", 13400))
        raise socket.timeout

    mock_sock.recvfrom.side_effect = mock_recvfrom

    # Call the function
    ecus = discover_ecus(timeout=0.1)

    # Assertions
    assert len(ecus) == 1
    ecu_info = ecus[0]
    assert isinstance(ecu_info, ECUInfo)
    assert ecu_info.ip == "192.168.1.3"
    assert ecu_info.logical_address == 0x1002
    assert ecu_info.eid == b"EID456"

    # Verify socket operations were called
    mock_sock.sendto.assert_called_once()
    mock_sock.close.assert_called_once()


@patch("udsonip.discovery.Parser")
@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_timeout(MockDoIPClient, MockParser):
    """Test discover_ecus when no ECUs are found."""
    # Create mock socket
    mock_sock = MagicMock()
    MockDoIPClient._create_udp_socket.return_value = mock_sock
    MockDoIPClient._pack_doip.return_value = b"packed_data"

    # Mock socket.recvfrom to always raise timeout
    mock_sock.recvfrom.side_effect = socket.timeout

    # Call the function
    ecus = discover_ecus(timeout=0.1)

    # Assertions
    assert len(ecus) == 0
    mock_sock.sendto.assert_called_once()
    mock_sock.close.assert_called_once()


@patch("udsonip.discovery.Parser")
@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_broadcast_failure(MockDoIPClient, MockParser):
    """Test discover_ecus when sendto fails but socket creation succeeds."""
    # Create mock socket
    mock_sock = MagicMock()
    MockDoIPClient._create_udp_socket.return_value = mock_sock
    MockDoIPClient._pack_doip.return_value = b"packed_data"

    # Mock sendto to fail
    mock_sock.sendto.side_effect = Exception("Network unreachable")

    # Call the function - should raise DiscoveryError
    from udsonip.exceptions import DiscoveryError

    with pytest.raises(DiscoveryError, match="ECU discovery failed"):
        discover_ecus(timeout=0.1)

    mock_sock.close.assert_called_once()


@patch("udsonip.discovery.Parser")
@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_duplicate_filtering(MockDoIPClient, MockParser):
    """Test that discover_ecus filters duplicate ECUs."""
    # Mock announcement - same ECU announced multiple times
    mock_announcement = VehicleIdentificationResponse(
        vin=b"TESTVIN123456789",
        logical_address=0x3001,
        eid=b"EIDDUP",
        gid=b"GIDDUP",
        further_action_required=0x00,
    )

    # Create mock socket
    mock_sock = MagicMock()
    MockDoIPClient._create_udp_socket.return_value = mock_sock
    MockDoIPClient._pack_doip.return_value = b"packed_data"

    # Mock parser to return the same announcement
    mock_parser_instance = MockParser.return_value
    mock_parser_instance.read_message.return_value = mock_announcement

    # Mock socket.recvfrom to return same data 3 times, then timeout
    call_count = {"count": 0}

    def mock_recvfrom(size):
        call_count["count"] += 1
        if call_count["count"] <= 3:
            return (b"response_data", ("192.168.1.10", 13400))
        raise socket.timeout

    mock_sock.recvfrom.side_effect = mock_recvfrom

    # Call the function
    ecus = discover_ecus(timeout=0.1)

    # Should only have one ECU (duplicates filtered)
    assert len(ecus) == 1
    assert ecus[0].ip == "192.168.1.10"
    assert ecus[0].logical_address == 0x3001


@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_discovery_error(MockDoIPClient):
    """Test that discover_ecus raises DiscoveryError on socket creation failure."""
    from udsonip.exceptions import DiscoveryError

    # Mock socket creation to fail
    MockDoIPClient._create_udp_socket.side_effect = Exception("Socket creation failed")

    with pytest.raises(DiscoveryError, match="ECU discovery failed"):
        discover_ecus()


@patch("udsonip.discovery.DoIPClient")
def test_discover_ecus_generic_error(MockDoIPClient):
    """Test that discover_ecus wraps a generic exception in DiscoveryError."""
    from udsonip.exceptions import DiscoveryError

    # Create mock socket
    mock_sock = MagicMock()
    MockDoIPClient._create_udp_socket.return_value = mock_sock

    # Mock _pack_doip to fail
    MockDoIPClient._pack_doip.side_effect = Exception("Packing failed")

    with pytest.raises(DiscoveryError, match="ECU discovery failed"):
        discover_ecus()


@patch("udsonip.discovery.DoIPClient")
def test_get_entity_generic_exception(MockDoIPClient):
    """Test that get_entity wraps a generic exception in DiscoveryError."""
    from udsonip.exceptions import DiscoveryError

    MockDoIPClient.get_entity.side_effect = Exception("Generic network error")

    with pytest.raises(
        DiscoveryError,
        match="Failed to get entity info from 192.168.1.1: Generic network error",
    ):
        get_entity(ip="192.168.1.1")
