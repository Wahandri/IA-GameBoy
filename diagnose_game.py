import time
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"
ADDR_LIVES = 0xC699

def main():
    print("Initializing PyBoy...")
    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(1)
    
    print("\n--- DIAGNOSTIC MODE ---")
    print("1. Play the game.")
    print("2. Watch the terminal output.")
    print("3. When you get points, look for changed values.")
    print("4. When you reach the 'Continue' screen, look at the 'Lives' value.")
    
    # Potential Score Addresses (Scanning C600-C6FF as it's near Lives)
    # and C000-C100 (Common Work RAM start)
    watched_addresses = list(range(0xC600, 0xC700)) + list(range(0xC000, 0xC100))
    previous_memory = {addr: pyboy.memory[addr] for addr in watched_addresses}
    
    while True:
        pyboy.tick()
        
        if pyboy.frame_count % 60 == 0: # Every 1 second approx
            lives = pyboy.memory[ADDR_LIVES]
            print(f"Current Lives Value: {lives}")
            
            # Check for changes in watched addresses
            changes = []
            for addr in watched_addresses:
                val = pyboy.memory[addr]
                if val != previous_memory[addr]:
                    changes.append((addr, val))
                    previous_memory[addr] = val
            
            if changes:
                print("Memory Changes (Potential Score?):")
                for addr, val in changes[:10]: # Show first 10 changes
                    print(f"  0x{addr:04X}: {val}")
                if len(changes) > 10:
                    print(f"  ... and {len(changes)-10} more.")
                    
        time.sleep(0.001)

if __name__ == "__main__":
    main()
