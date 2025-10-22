"""
ECU discovery example.
"""

from udsonip import discover_ecus

def main():
    print("Discovering ECUs on the network...")
    print("(This may take a few seconds)")
    
    # Discover ECUs
    ecus = discover_ecus(timeout=5.0)
    
    if not ecus:
        print("\n❌ No ECUs found")
        return
    
    print(f"\n✓ Found {len(ecus)} ECU(s):\n")
    
    for i, ecu in enumerate(ecus, 1):
        print(f"{i}. {ecu}")
        print(f"   IP: {ecu.ip}")
        print(f"   Address: {ecu.logical_address:#x}")
        if ecu.eid:
            print(f"   EID: {ecu.eid.hex()}")
        if ecu.gid:
            print(f"   GID: {ecu.gid.hex()}")
        print()
    
    # Connect to first discovered ECU
    if ecus:
        print(f"Connecting to first ECU: {ecus[0]}")
        client = ecus[0].connect()
        
        try:
            # Read VIN
            response = client.read_data_by_identifier(0xF190)
            vin = response.data.decode('ascii', errors='ignore')
            print(f"✓ VIN: {vin}")
        finally:
            client.close()


if __name__ == '__main__':
    main()
