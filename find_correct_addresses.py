"""
Script mejorado para encontrar las direcciones correctas de Super Mario Land.

INSTRUCCIONES:
1. Ejecuta: python3 find_correct_addresses.py
2. Observa la pantalla del juego - debería mostrar MARIO×02 (2 vidas al inicio)
3. El script buscará en TODA la memoria valores que coincidan con 2
4. Cuando pierdas una vida, busca qué dirección cambió de 2 a 1
5. Anota la dirección correcta
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/super-mario-land.gb"
WINDOW_TYPE = "SDL2"

def main():
    print("="*70)
    print("BUSCADOR COMPLETO DE DIRECCIONES - SUPER MARIO LAND")
    print("="*70)
    print("\n🔍 Este script buscará en TODA la RAM valores que coincidan con")
    print("   lo que ves en pantalla (MARIO×02 = 2 vidas)")
    print("\n📋 Al inicio deberías ver MARIO×02 en pantalla")
    print("   Buscaremos direcciones que contengan el valor 2\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    # Esperar a que cargue el juego
    print("Esperando a que cargue el juego...")
    for _ in range(300):
        pyboy.tick()
    
    print("\n🎮 JUEGA MANUALMENTE Y OBSERVA:")
    print("   1. Cuando veas MARIO×02 (2 vidas), anota qué direcciones tienen valor 2")
    print("   2. Cuando pierdas una vida y veas MARIO×01, anota cuál cambió a 1")
    print("   3. Esa será la dirección correcta de Lives\n")
    
    # Monitorear rangos completos de WRAM
    ranges = [
        (0xC000, 0xC0FF, "WRAM Bank 0 - Parte 1"),
        (0xC100, 0xC1FF, "WRAM Bank 0 - Parte 2"),
        (0xC200, 0xC2FF, "WRAM Bank 0 - Parte 3"),
        (0xC300, 0xC3FF, "WRAM Bank 0 - Parte 4"),
        (0xDA00, 0xDAFF, "WRAM Bank 1"),
        (0xDB00, 0xDBFF, "WRAM Bank 2"),
    ]
    
    # Diccionario para trackear valores
    memory_snapshot = {}
    
    # Tomar snapshot inicial
    for start, end, _ in ranges:
        for addr in range(start, end + 1):
            memory_snapshot[addr] = pyboy.memory[addr]
    
    step_count = 0
    
    while True:
        pyboy.tick()
        step_count += 1
        
        if step_count % 60 == 0:  # Cada ~1 segundo
            print(f"\n{'='*70}")
            print(f"Frame: {pyboy.frame_count} - Buscando direcciones con valores pequeños (0-10)")
            print(f"{'='*70}")
            
            # Buscar direcciones con valores pequeños (0-10) que puedan ser vidas
            candidates = []
            
            for start, end, range_name in ranges:
                range_candidates = []
                
                for addr in range(start, end + 1):
                    val = pyboy.memory[addr]
                    old_val = memory_snapshot[addr]
                    
                    # Buscar valores pequeños (típicos de vidas/niveles)
                    if 0 <= val <= 10:
                        changed = "***CAMBIÓ***" if val != old_val else ""
                        range_candidates.append({
                            'addr': addr,
                            'val': val,
                            'old': old_val,
                            'changed': changed
                        })
                    
                    memory_snapshot[addr] = val
                
                if range_candidates:
                    candidates.append((range_name, range_candidates))
            
            # Mostrar candidatos agrupados
            for range_name, range_candidates in candidates:
                print(f"\n📍 [{range_name}]:")
                
                # Mostrar solo los primeros 10 de cada rango
                for i, cand in enumerate(range_candidates[:10]):
                    addr = cand['addr']
                    val = cand['val']
                    old = cand['old']
                    changed = cand['changed']
                    
                    print(f"   0x{addr:04X} = {val:2d} (era {old:2d}) {changed}")
                
                if len(range_candidates) > 10:
                    print(f"   ... y {len(range_candidates) - 10} más")
            
            print(f"\n💡 PISTA: Busca una dirección que:")
            print(f"   - Tenga valor 2 cuando veas MARIO×02")
            print(f"   - Cambie a 1 cuando veas MARIO×01")
            print(f"   - Cambie a 0 cuando veas GAME OVER")
        
        time.sleep(0.001)

if __name__ == "__main__":
    main()
