"""
Script para encontrar las direcciones de memoria de los enemigos en Snow Bros.

INSTRUCCIONES:
1. Ejecuta: python3 find_enemies.py
2. Juega normalmente
3. Observa qué direcciones cambian cuando aparecen/desaparecen enemigos
4. Los enemigos típicamente tienen coordenadas X, Y y un flag de "activo"
5. Anota las direcciones que veas cambiar consistentemente
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"
WINDOW_TYPE = "SDL2"

# Addresses conocidas
ADDR_LIVES = 0xC699
ADDR_PLAYER_X = 0xC1A0
ADDR_PLAYER_Y = 0xC1A2

def main():
    print("="*70)
    print("BUSCADOR DE ENEMIGOS - SNOW BROS")
    print("="*70)
    print("\n📋 Este script mostrará cambios en memoria para encontrar enemigos")
    print("🎮 JUEGA NORMALMENTE y observa cuando aparezcan/mueran enemigos\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    # Monitorear área amplia donde podrían estar los enemigos
    # Típicamente los enemigos están cerca del player en memoria
    watch_ranges = [
        (0xC180, 0xC1FF, "Rango Player"),  # Cerca del jugador
        (0xC200, 0xC27F, "Rango 1"),       # Posible área de enemigos
        (0xC280, 0xC2FF, "Rango 2"),       # Otra área posible
    ]
    
    previous_memory = {}
    
    # Inicializar diccionario de memoria previa
    for start, end, _ in watch_ranges:
        for addr in range(start, end + 1):
            previous_memory[addr] = pyboy.memory[addr]
    
    step_count = 0
    significant_changes = []
    
    while True:
        pyboy.tick()
        step_count += 1
        
        if step_count % 30 == 0:  # Cada ~0.5 segundos
            px = pyboy.memory[ADDR_PLAYER_X]
            py = pyboy.memory[ADDR_PLAYER_Y]
            lives = pyboy.memory[ADDR_LIVES]
            
            print(f"\n{'='*70}")
            print(f"Player: ({px:3d}, {py:3d}) | Lives: {lives}")
            print(f"{'='*70}")
            
            all_changes = []
            
            for start, end, range_name in watch_ranges:
                changes_in_range = []
                
                for addr in range(start, end + 1):
                    val = pyboy.memory[addr]
                    
                    if val != previous_memory[addr]:
                        old_val = previous_memory[addr]
                        changes_in_range.append({
                            'addr': addr,
                            'old': old_val,
                            'new': val,
                            'diff': abs(val - old_val)
                        })
                        previous_memory[addr] = val
                
                if changes_in_range:
                    all_changes.append((range_name, changes_in_range))
            
            # Mostrar cambios agrupados por rango
            if all_changes:
                print(f"\n🔔 CAMBIOS DETECTADOS:")
                for range_name, changes in all_changes:
                    print(f"\n  [{range_name}] - {len(changes)} cambios:")
                    
                    # Mostrar los primeros 5 cambios de cada rango
                    for change in changes[:5]:
                        addr = change['addr']
                        old = change['old']
                        new = change['new']
                        
                        # Resaltar cambios significativos (podrían ser posiciones)
                        if 0 < new < 200 and abs(new - old) < 50:
                            marker = "⭐ POSIBLE COORD"
                        else:
                            marker = ""
                        
                        print(f"    0x{addr:04X}: {old:3d} → {new:3d}  {marker}")
                    
                    if len(changes) > 5:
                        print(f"    ... y {len(changes) - 5} cambios más")
            else:
                print("  (sin cambios)")
            
            # Buscar patrones que parezcan coordenadas (valores 0-255, cambios pequeños)
            if step_count % 90 == 0:  # Cada ~1.5 segundos
                print(f"\n💡 SUGERENCIA: Intenta matar un enemigo para ver cambios claros")
        
        time.sleep(0.001)

if __name__ == "__main__":
    main()
