"""
Script para encontrar las direcciones correctas de Score y Game Over.

INSTRUCCIONES:
1. Ejecuta: python3 find_game_over.py
2. Juega normalmente
3. Cuando ganes puntos, observa qué direcciones cambian
4. Cuando llegues a GAME OVER (display vacío), observa qué valor tiene Lives
5. Copia y pega los valores que veas en la terminal
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"
WINDOW_TYPE = "SDL2"

ADDR_LIVES = 0xC699

def main():
    print("="*70)
    print("DIAGNÓSTICO DE MEMORIA - SNOW BROS")
    print("="*70)
    print("\n📋 Este script mostrará:")
    print("  1. Valor de Lives (0xC699)")
    print("  2. Valores alrededor de Lives (para encontrar Score)")
    print("  3. Te dirá cuando detecte cambios\n")
    print("🎮 JUEGA NORMALMENTE y observa la terminal\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    # Monitorear área alrededor de Lives
    # Lives está en 0xC699, score debería estar cerca "a la derecha"
    watch_start = 0xC698  # Un poco antes de Lives
    watch_end = 0xC6A5    # Bastante después de Lives
    
    previous_memory = {}
    for addr in range(watch_start, watch_end + 1):
        previous_memory[addr] = pyboy.memory[addr]
    
    step_count = 0
    
    while True:
        pyboy.tick()
        step_count += 1
        
        if step_count % 30 == 0:  # Cada ~0.5 segundos
            lives = pyboy.memory[ADDR_LIVES]
            
            # Mostrar área de memoria completa
            print(f"\n{'='*70}")
            print(f"Lives = {lives:3d} (0x{lives:02X})")
            print(f"{'='*70}")
            print("Dirección | Valor Dec | Valor Hex | Estado")
            print("-"*70)
            
            changes = []
            for addr in range(watch_start, watch_end + 1):
                val = pyboy.memory[addr]
                changed = "*** CAMBIÓ ***" if val != previous_memory[addr] else ""
                
                # Marcar Lives claramente
                if addr == ADDR_LIVES:
                    label = "LIVES -->"
                else:
                    offset = addr - ADDR_LIVES
                    if offset > 0:
                        label = f"+{offset:2d}    "
                    else:
                        label = f"{offset:3d}    "
                
                print(f"0x{addr:04X} {label} | {val:8d} | 0x{val:02X}      | {changed}")
                
                if val != previous_memory[addr]:
                    changes.append((addr, previous_memory[addr], val))
                
                previous_memory[addr] = val
            
            # Resumen de cambios
            if changes:
                print(f"\n🔔 CAMBIOS DETECTADOS:")
                for addr, old_val, new_val in changes:
                    offset = addr - ADDR_LIVES
                    if offset == 0:
                        pos = "Lives"
                    elif offset > 0:
                        pos = f"Lives+{offset}"
                    else:
                        pos = f"Lives{offset}"
                    print(f"   0x{addr:04X} ({pos}): {old_val} -> {new_val}")
            
            # Alertas especiales
            if lives == 0:
                print(f"\n⚠️  Lives = 0 detectado")
            elif lives == 255:
                print(f"\n⚠️  Lives = 255 (0xFF) detectado")
            elif lives > 10:
                print(f"\n⚠️  Lives = {lives} (valor inusual)")
                
        time.sleep(0.001)

if __name__ == "__main__":
    main()
