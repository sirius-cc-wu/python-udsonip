"""
Dynamic address switching example.
"""

from udsonip import DoIPUDSClient

def main():
    # Create client
    client = DoIPUDSClient(
        ecu_ip='192.168.1.10',
        ecu_address=0x00E0  # Start with engine ECU
    )
    
    try:
        print("=== Initial target: Engine (0x00E0) ===")
        response = client.read_data_by_identifier(0xF190)
        print(f"VIN: {response.data.decode('ascii', errors='ignore')}")
        
        # Switch to transmission ECU
        print("\n=== Switching to Transmission (0x00E1) ===")
        client.target_address = 0x00E1
        response = client.read_data_by_identifier(0xF190)
        print(f"VIN: {response.data.decode('ascii', errors='ignore')}")
        
        # Switch to ABS ECU
        print("\n=== Switching to ABS (0x00E2) ===")
        client.target_address = 0x00E2
        response = client.tester_present()
        print(f"TesterPresent: {response}")
        
        # Switch back to engine
        print("\n=== Switching back to Engine (0x00E0) ===")
        client.target_address = 0x00E0
        response = client.read_data_by_identifier(0xF195)
        print(f"Software version: {response.data.hex()}")
        
        print(f"\n✓ Successfully communicated with {client.target_address:#x}")
        
    finally:
        client.close()


if __name__ == '__main__':
    main()
