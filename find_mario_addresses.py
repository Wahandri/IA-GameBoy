"""
Script para encontrar y verificar direcciones de memoria en Super Mario Land.

INSTRUCCIONES:
1. Ejecuta: python3 find_mario_addresses.py
2. Juega normalmente con las teclas del teclado
3. Observa cómo cambian las direcciones cuando:
   - Ganas/pierdes vidas
   - Ganas puntos (monedas, enemigos)
   - Te mueves (posición X, Y)
   - Cambias de nivel/mundo
4. Anota las direcciones que funcionan correctamente
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/super-mario-land.gb"
WINDOW_TYPE = "SDL2"

# Direcciones documentadas de Super Mario Land
ADDR_LIVES = 0xDA15          # Vidas
ADDR_SCORE_START = 0xC0A0    # Score (BCD, 3 bytes)
ADDR_PLAYER_X = 0xC202       # Posición X (screen-relative)
ADDR_PLAYER_Y = 0xC201       # Posición Y (screen-relative)
ADDR_WORLD = 0xC0A4          # Mundo actual
ADDR_LEVEL = 0xC0A5          # Nivel actual

def read_score_bcd(memory):
    """Lee el score en formato BCD (3 bytes)."""
    score_bytes = [
        memory[0xC0A0],
        memory[0xC0A1],
        memory[0xC0A2],
    ]
    
    score = 0
    for byte_val in score_bytes:
        high = (byte_val >> 4) & 0x0F
        low = byte_val & 0x0F
        score = score * 100 + high * 10 + low
    
    return score

def main():
    print("="*70)
    print("DIAGNÓSTICO DE MEMORIA - SUPER MARIO LAND")
    print("="*70)
    print("\n📋 Direcciones documentadas que verificaremos:")
    print(f"  Lives:     0x{ADDR_LIVES:04X}")
    print(f"  Score:     0x{ADDR_SCORE_START:04X}-0x{ADDR_SCORE_START+2:04X}")
    print(f"  Player X:  0x{ADDR_PLAYER_X:04X}")
    print(f"  Player Y:  0x{ADDR_PLAYER_Y:04X}")
    print(f"  World:     0x{ADDR_WORLD:04X}")
    print(f"  Level:     0x{ADDR_LEVEL:04X}")
    print("\n🎮 JUEGA NORMALMENTE y observa la terminal\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    previous_values = {
        'lives': 0,
        'score': 0,
        'x': 0,
        'y': 0,
        'world': 0,
        'level': 0,
    }
    
    step_count = 0
    
    while True:
        pyboy.tick()
        step_count += 1
        
        if step_count % 30 == 0:  # Cada ~0.5 segundos
            lives = pyboy.memory[ADDR_LIVES]
            score = read_score_bcd(pyboy.memory)
            px = pyboy.memory[ADDR_PLAYER_X]
            py = pyboy.memory[ADDR_PLAYER_Y]
            world = pyboy.memory[ADDR_WORLD]
            level = pyboy.memory[ADDR_LEVEL]
            
            # Mostrar estado actual
            print(f"\n{'='*70}")
            print(f"Frame: {pyboy.frame_count}")
            print(f"{'='*70}")
            print(f"Lives:     {lives:3d} (0x{lives:02X})", end="")
            if lives != previous_values['lives']:
                print(f"  *** CAMBIÓ de {previous_values['lives']} ***", end="")
            print()
            
            print(f"Score:     {score:6d}", end="")
            if score != previous_values['score']:
                print(f"  *** CAMBIÓ +{score - previous_values['score']} ***", end="")
            print()
            
            print(f"Position:  X={px:3d} (0x{px:02X}), Y={py:3d} (0x{py:02X})", end="")
            if px != previous_values['x'] or py != previous_values['y']:
                print(f"  *** MOVIMIENTO ***", end="")
            print()
            
            print(f"World-Level: {world}-{level}", end="")
            if world != previous_values['world'] or level != previous_values['level']:
                print(f"  *** CAMBIÓ DE NIVEL ***", end="")
            print()
            
            # Actualizar valores previos
            previous_values['lives'] = lives
            previous_values['score'] = score
            previous_values['x'] = px
            previous_values['y'] = py
            previous_values['world'] = world
            previous_values['level'] = level
            
            # Alertas
            if lives == 0:
                print(f"\n⚠️  Lives = 0 (GAME OVER?)")
        
        time.sleep(0.001)

if __name__ == "__main__":
    main()
