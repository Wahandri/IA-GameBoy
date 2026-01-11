import time
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"
WINDOW_TYPE = "SDL2"

# Addresses from your main.py
ADDR_LIVES = 0xC699
ADDR_PLAYER_X = 0xC1A0
ADDR_PLAYER_Y = 0xC1A2

def main():
    print("--- DIAGNOSTICO DE GAME OVER ---")
    print("1. El juego se iniciará.")
    print("2. Juega normal hasta perder todas las vidas.")
    print("3. Cuando salga la pantalla de 'CONTINUE' (cuenta atrás), observa los valores en la terminal.")
    print("4. Copia y pega esos valores en el chat.")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    while True:
        pyboy.tick()
        
        if pyboy.frame_count % 30 == 0: # Cada 0.5 segundos
            lives = pyboy.memory[ADDR_LIVES]
            px = pyboy.memory[ADDR_PLAYER_X]
            py = pyboy.memory[ADDR_PLAYER_Y]
            
            print(f"Vidas: {lives} | PosX: {px} | PosY: {py}")
            
        time.sleep(0.001)

if __name__ == "__main__":
    main()
