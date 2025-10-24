import pytest
import warnings
from unittest.mock import patch, MagicMock
from doipclient.messages import VehicleIdentificationResponse
from udsonip.discovery import ECUInfo, get_entity, discover_ecus


class TestECUInfo:
    """Tests for ECUInfo dataclass."""
    
    def test_init(self):
        """Test ECUInfo initialization."""
        ecu = ECUInfo(
            ip='192.168.1.10',
            logical_address=0x00E0,
            eid=b'VIN12345678901234',
            gid=b'\x00\x01'
        )
        
        assert ecu.ip == '192.168.1.10'
        assert ecu.logical_address == 0x00E0
        assert ecu.eid == b'VIN12345678901234'
        assert ecu.gid == b'\x00\x01'
    
    def test_str(self):
        """Test string representation."""
        ecu = ECUInfo(ip='192.168.1.10', logical_address=0x00E0)
        assert str(ecu) == "ECU(192.168.1.10 @ 0x00E0)"
    
    def test_repr(self):
        """Test repr representation."""
        ecu = ECUInfo(ip='192.168.1.10', logical_address=0x00E0)
        assert repr(ecu) == "ECUInfo(ip='192.168.1.10', logical_address=0x00E0)"


@patch('udsonip.discovery.DoIPClient')
def test_get_entity_found(MockDoIPClient):
    """Test get_entity when an ECU is found."""
    # Mock the announcement message
    mock_announcement = VehicleIdentificationResponse(
        vin=b'TESTVIN123456789',
        logical_address=0x1001,
        eid=b'EID123',
        gid=b'GID123',
        further_action_required=0x00
    )
    
    # Configure the mock DoIPClient
    mock_instance = MockDoIPClient.return_value
    MockDoIPClient.get_entity.return_value = (('192.168.1.1', 13400), mock_announcement)
    
    # Call the function
    ecu_info = get_entity(ip='192.168.1.1')
    
    # Assertions
    assert isinstance(ecu_info, ECUInfo)
    assert ecu_info.ip == '192.168.1.1'
    assert ecu_info.logical_address == 0x1001
    assert ecu_info.eid == b'EID123'
    assert ecu_info.gid == b'GID123'
    MockDoIPClient.get_entity.assert_called_once_with(
        ip='192.168.1.1',
        timeout=2.0,
        protocol_version=0x03
    )


@patch('udsonip.discovery.DoIPClient')
def test_get_entity_not_found(MockDoIPClient):
    """Test get_entity when no ECU is found (timeout)."""
    # Configure the mock to raise a TimeoutError
    MockDoIPClient.get_entity.side_effect = TimeoutError
    
    # Call the function
    ecu_info = get_entity(ip='192.168.1.2')
    
    # Assertions
    assert ecu_info is None
    MockDoIPClient.get_entity.assert_called_once_with(
        ip='192.168.1.2',
        timeout=2.0,
        protocol_version=0x03
    )


@patch('udsonip.discovery.DoIPClient')
def test_discover_ecus_found(MockDoIPClient):
    """Test discover_ecus when a single ECU is found."""
    # Mock the announcement message
    mock_announcement = VehicleIdentificationResponse(
        vin=b'TESTVIN123456789',
        logical_address=0x1002,
        eid=b'EID456',
        gid=b'GID456',
        further_action_required=0x00
    )
    
    # Configure the mock: request succeeds
    MockDoIPClient.request_vehicle_identification.return_value = None
    
    # Track call count to return announcement once, then timeouts
    call_count = {'count': 0}
    def mock_await(*args, **kwargs):
        call_count['count'] += 1
        if call_count['count'] == 1:
            return (('192.168.1.3', 13400), mock_announcement)
        raise TimeoutError
    
    MockDoIPClient.await_vehicle_announcement.side_effect = mock_await
    
    # Call the function
    ecus = discover_ecus(timeout=0.1)
    
    # Assertions
    assert len(ecus) == 1
    ecu_info = ecus[0]
    assert isinstance(ecu_info, ECUInfo)
    assert ecu_info.ip == '192.168.1.3'
    assert ecu_info.logical_address == 0x1002
    assert ecu_info.eid == b'EID456'
    
    # Verify that request_vehicle_identification was called
    MockDoIPClient.request_vehicle_identification.assert_called_once()


@patch('udsonip.discovery.DoIPClient')
def test_discover_ecus_timeout(MockDoIPClient):
    """Test discover_ecus when no ECUs are found."""
    # Configure the mock: request succeeds but no announcements received
    MockDoIPClient.request_vehicle_identification.return_value = None
    MockDoIPClient.await_vehicle_announcement.side_effect = TimeoutError
    
    # Call the function
    ecus = discover_ecus(timeout=0.1)
    
    # Assertions
    assert len(ecus) == 0
    MockDoIPClient.request_vehicle_identification.assert_called_once()


@patch('udsonip.discovery.DoIPClient')
def test_discover_ecus_broadcast_failure(MockDoIPClient):
    """Test discover_ecus when broadcast fails but listening still works."""
    # Mock the announcement message
    mock_announcement = VehicleIdentificationResponse(
        vin=b'TESTVIN123456789',
        logical_address=0x2001,
        eid=b'EID789',
        gid=b'GID789',
        further_action_required=0x00
    )
    
    # Configure the mock: request fails
    MockDoIPClient.request_vehicle_identification.side_effect = Exception("Broadcast failed")
    
    # Return announcement once, then timeouts
    call_count = {'count': 0}
    def mock_await(*args, **kwargs):
        call_count['count'] += 1
        if call_count['count'] == 1:
            return (('192.168.1.5', 13400), mock_announcement)
        raise TimeoutError
    
    MockDoIPClient.await_vehicle_announcement.side_effect = mock_await
    
    # Call the function - should warn but continue
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ecus = discover_ecus(timeout=0.1)
        
        # Verify warning was raised
        assert len(w) == 1
        assert "Failed to broadcast" in str(w[0].message)
    
    # Should still find the ECU from spontaneous announcement
    assert len(ecus) == 1
    assert ecus[0].logical_address == 0x2001


@patch('udsonip.discovery.DoIPClient')
def test_discover_ecus_duplicate_filtering(MockDoIPClient):
    """Test that discover_ecus filters duplicate ECUs."""
    # Mock announcement - same ECU announced multiple times
    mock_announcement = VehicleIdentificationResponse(
        vin=b'TESTVIN123456789',
        logical_address=0x3001,
        eid=b'EIDDUP',
        gid=b'GIDDUP',
        further_action_required=0x00
    )
    
    # Configure the mock: request succeeds
    MockDoIPClient.request_vehicle_identification.return_value = None
    
    # Return same announcement 3 times, then timeouts
    call_count = {'count': 0}
    def mock_await(*args, **kwargs):
        call_count['count'] += 1
        if call_count['count'] <= 3:
            return (('192.168.1.10', 13400), mock_announcement)
        raise TimeoutError
    
    MockDoIPClient.await_vehicle_announcement.side_effect = mock_await
    
    # Call the function
    ecus = discover_ecus(timeout=0.1)
    
    # Should only have one ECU (duplicates filtered)
    assert len(ecus) == 1
    assert ecus[0].ip == '192.168.1.10'
    assert ecus[0].logical_address == 0x3001
