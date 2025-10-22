"""
Basic example: Single ECU communication using udsonip.
"""

from udsonip import DoIPUDSClient

def main():
    # Create client connected to a single ECU
    client = DoIPUDSClient(
        ecu_ip='192.168.1.10',
        ecu_address=0x00E0  # Engine ECU
    )
    
    try:
        # Send tester present
        print("Sending TesterPresent...")
        response = client.tester_present()
        print(f"✓ TesterPresent response: {response}")
        
        # Read VIN (Data Identifier 0xF190)
        print("\nReading VIN...")
        response = client.read_data_by_identifier(0xF190)
        vin = response.data.decode('ascii', errors='ignore')
        print(f"✓ VIN: {vin}")
        
        # Read ECU software version (DID 0xF195)
        print("\nReading software version...")
        response = client.read_data_by_identifier(0xF195)
        version = response.data.hex()
        print(f"✓ Software Version: {version}")
        
        # Read active DTCs
        print("\nReading DTCs...")
        response = client.read_dtc_information()
        print(f"✓ DTCs: {response}")
        
    finally:
        # Always close the connection
        client.close()
        print("\n✓ Connection closed")


if __name__ == '__main__':
    main()
