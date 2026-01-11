import sys
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"

def scan_memory(pyboy, target_value, candidates=None):
    """
    Scans memory for a specific value.
    If candidates is None, scans all WRAM (0xC000 - 0xDFFF).
    If candidates is a list, filters that list.
    """
    new_candidates = []
    memory = pyboy.memory
    
    if candidates is None:
        # Initial scan of WRAM
        # WRAM size is 8KB (0xC000 to 0xDFFF)
        print("Scanning full WRAM (0xC000 - 0xDFFF)...")
        for addr in range(0xC000, 0xE000):
            val = memory[addr]
            if val == target_value:
                new_candidates.append(addr)
    else:
        # Filter existing candidates
        print(f"Filtering {len(candidates)} candidates...")
        for addr in candidates:
            val = memory[addr]
            if val == target_value:
                new_candidates.append(addr)
                
    return new_candidates

def main():
    print("Initializing PyBoy...")
    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(1)
    
    print("\n--- MEMORY FINDER TOOL ---")
    print("Controls:")
    print("  Play the game in the window.")
    print("  Focus this terminal and press ENTER when ready for a step.")
    
    # --- LIVES SCANNING ---
    print("\n[STEP 1] LIVES SCANNER")
    input("1. Start the game and ensure you have exactly 3 LIVES. Press ENTER when ready.")
    
    candidates = scan_memory(pyboy, 3)
    print(f"Found {len(candidates)} addresses with value 3.")
    
    if len(candidates) > 0:
        input("2. Now lose a life (so you have 2 LIVES). Press ENTER when ready.")
        candidates = scan_memory(pyboy, 2, candidates)
        print(f"Found {len(candidates)} addresses with value 2.")
        
        if len(candidates) > 0:
            print("Potential LIVES addresses:")
            for addr in candidates:
                print(f"  0x{addr:04X}")
        else:
            print("No matches found. Maybe lives are stored differently (e.g., 0-indexed: 2 means 3 lives).")
    else:
        print("No addresses found with value 3.")

    # --- SCORE SCANNING (Simplified) ---
    print("\n[STEP 2] SCORE SCANNER (Low Byte)")
    print("We will look for the score. Note: Score might be BCD (Binary Coded Decimal) or standard integer.")
    input("1. Start a new game or reset. Ensure Score is 0. Press ENTER.")
    
    score_candidates = scan_memory(pyboy, 0)
    print(f"Found {len(score_candidates)} addresses with value 0.")
    
    input("2. Get some points (e.g., kill an enemy). Try to get exactly 100 points if possible, or just any points. Press ENTER.")
    # Here we can't search for a specific value easily without asking the user.
    # Let's just look for changed values.
    
    changed_candidates = []
    for addr in score_candidates:
        if pyboy.memory[addr] > 0:
            changed_candidates.append(addr)
            
    print(f"Found {len(changed_candidates)} addresses that increased from 0.")
    print("Potential SCORE addresses (first 20):")
    for addr in changed_candidates[:20]:
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")

    pyboy.stop()

if __name__ == "__main__":
    main()
