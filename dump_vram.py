"""
Script para volcar el contenido de la VRAM (Tile Map) y encontrar texto en pantalla.

INSTRUCCIONES:
1. Ejecuta: python3 dump_vram.py
2. Juega hasta que aparezca "GAME OVER" en la pantalla.
3. Observa la salida de la terminal. El script mostrará los Tile IDs.
4. Busca patrones que se repitan o parezcan texto.
   Por ejemplo, si ves una secuencia que se mantiene constante cuando dice GAME OVER, esos son los IDs.
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/super-mario-land.gb"
WINDOW_TYPE = "SDL2"

# Rango del Background Map en VRAM (normalmente 0x9800 - 0x9BFF para Game Boy)
VRAM_START = 0x9800
VRAM_END = 0x9BFF
WIDTH = 32  # El mapa de tiles tiene 32 tiles de ancho

from pyboy.utils import WindowEvent

def main():
    print("="*70)
    print("DUMP DE VRAM (TILE MAP) - SUPER MARIO LAND")
    print("="*70)
    print("\n🎮 EL SCRIPT INICIARÁ EL JUEGO AUTOMÁTICAMENTE.")
    print("   Una vez en el juego, espera a morir o juega manualmente si la ventana tiene foco.")
    print("   (Controles: Flechas, A=Z, B=X, Start=Enter)\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    print("⏳ Iniciando juego (pulsando START)...")
    # Secuencia de inicio
    for _ in range(100): pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    for _ in range(10): pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    for _ in range(50): pyboy.tick()
    
    print("✅ Juego iniciado. Esperando Game Over...")
    print("📝 El log se guardará en 'vram_log.txt'")
    
    # Limpiar log anterior
    with open("vram_log.txt", "w") as f:
        f.write("VRAM DUMP LOG\n")
    
    while True:
        # Permitir que el juego corra
        pyboy.tick()
        
        # Cada 5 segundos (300 frames) para no saturar
        if pyboy.frame_count % 300 == 0:
            # Chequear posible flag de Game Over en RAM
            game_over_flag = pyboy.memory[0xC0A4]
            
            output = []
            output.append(f"\n{'='*70}")
            output.append(f"Frame: {pyboy.frame_count} | Flag Game Over (0xC0A4): {game_over_flag:02X}")
            output.append(f"{'='*70}")
            
            # Leer VRAM
            vram_data = [pyboy.memory[addr] for addr in range(VRAM_START, VRAM_END + 1)]
            
            # Mostrar como matriz de texto
            for y in range(18):
                row_data = vram_data[y*WIDTH : (y+1)*WIDTH]
                
                if any(tile > 0 and tile != 0xFF for tile in row_data):
                    hex_str = " ".join([f"{tile:02X}" for tile in row_data[:20]])
                    output.append(f"Fila {y:2d}: {hex_str}")
            
            output.append("\n")
            final_text = "\n".join(output)
            
            # Imprimir en pantalla y guardar en archivo
            print(final_text)
            with open("vram_log.txt", "a") as f:
                f.write(final_text)
        
        time.sleep(0.001)

if __name__ == "__main__":
    main()
