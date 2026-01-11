"""
Script simple para verificar direcciones específicas mientras juegas.

Ejecuta este script y JUEGA MANUALMENTE.
Verás en tiempo real los valores de varias direcciones candidatas.
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/super-mario-land.gb"
WINDOW_TYPE = "SDL2"

# Direcciones candidatas para Lives basadas en documentación
# Vamos a monitorear todas y ver cuál coincide con la pantalla
CANDIDATES = [
    0xDA15,  # Documentación dice aquí
    0xC0A3,  # También mencionado
    0x9806,  # Display de vidas
    0xFFB4,  # Otra posibilidad
    0xC0A0,  # Cerca de score
    0xC0A1,
    0xC0A2,
    0xDA14,
    0xDA16,
    0xDA17,
]

def main():
    print("="*70)
    print("VERIFICADOR DE VIDAS - Juega manualmente")
    print("="*70)
    print("\n🎮 INSTRUCCIONES:")
    print("   1. Juega con las flechas y botones del teclado")
    print("   2. Observa qué dirección muestra el valor correcto:")
    print("      - Debe mostrar 2 cuando veas MARIO×02")
    print("      - Debe cambiar a 1 cuando veas MARIO×01")
    print("   3. Anota la dirección correcta\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    # Esperar inicio
    for _ in range(300):
        pyboy.tick()
    
    previous_values = {addr: 0 for addr in CANDIDATES}
    
    while True:
        pyboy.tick()
        
        if pyboy.frame_count % 60 == 0:
            print(f"\n{'='*70}")
            print(f"Frame: {pyboy.frame_count}")
            print(f"Mira la pantalla - ¿Cuántas vidas ves? (MARIO×??)")
            print(f"{'='*70}")
            
            for addr in CANDIDATES:
                val = pyboy.memory[addr]
                old = previous_values[addr]
                
                changed = " *** CAMBIÓ ***" if val != old else ""
                
                # Resaltar si el valor parece razonable para vidas (0-10)
                marker = "  ⭐ CANDIDATO" if 0 <= val <= 10 else ""
                
                print(f"0x{addr:04X} = {val:3d} (0x{val:02X}) (era {old:3d}){changed}{marker}")
                
                previous_values[addr] = val
        
        time.sleep(0.001)

if __name__ == "__main__":
    main()
