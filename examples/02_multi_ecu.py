"""
Multi-ECU example: Communicating with multiple ECUs using udsonip.
"""

from udsonip import DoIPMultiECUClient

def main():
    # Create multi-ECU manager
    manager = DoIPMultiECUClient(gateway_ip='192.168.1.10')
    
    # Register ECUs
    manager.add_ecu('engine', 0x00E0)
    manager.add_ecu('transmission', 0x00E1)
    manager.add_ecu('abs', 0x00E2)
    manager.add_ecu('airbag', 0x00E3)
    
    try:
        print("Registered ECUs:")
        for name, address in manager.list_ecus().items():
            print(f"  - {name}: {address:#x}")
        
        # Communicate with engine ECU
        print("\n=== Engine ECU ===")
        with manager.ecu('engine') as ecu:
            response = ecu.read_data_by_identifier(0xF190)
            vin = response.data.decode('ascii', errors='ignore')
            print(f"VIN: {vin}")
            
            response = ecu.read_data_by_identifier(0xF195)
            print(f"Software: {response.data.hex()}")
        
        # Communicate with transmission ECU
        print("\n=== Transmission ECU ===")
        with manager.ecu('transmission') as ecu:
            response = ecu.read_data_by_identifier(0xF190)
            vin = response.data.decode('ascii', errors='ignore')
            print(f"VIN: {vin}")
            
            # Read transmission-specific data
            response = ecu.read_data_by_identifier(0x1234)  # Example DID
            print(f"Transmission status: {response.data.hex()}")
        
        # Communicate with ABS ECU
        print("\n=== ABS ECU ===")
        with manager.ecu('abs') as ecu:
            response = ecu.tester_present()
            print(f"TesterPresent: {response}")
            
            # Read DTCs from ABS
            response = ecu.read_dtc_information(
                services.ReadDTCInformation.Subfunction.reportDTCByStatusMask,
                0xFF
            )
            print(f"DTCs: {response}")
        
    finally:
        # Close all connections
        manager.close()
        print("\n✓ All connections closed")


if __name__ == '__main__':
    from udsoncan import services
    main()
