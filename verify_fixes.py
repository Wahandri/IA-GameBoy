"""
Script de verificación para los cambios en Snow Bros RL.

Este script muestra información útil en tiempo real para verificar:
1. Detección correcta de Game Over (lives=255 = display vacío)
2. Refuerzo positivo solo cuando el score aumenta

Instrucciones:
- Ejecuta este script: python verify_fixes.py
- Juega normalmente y observa la terminal
- Verifica que los mensajes de puntos solo aparecen cuando matas enemigos
- Pierde todas las vidas y verifica que game over se detecta correctamente
"""

import time
from pyboy import PyBoy

ROM_PATH = "roms/snow-bros.gb"
WINDOW_TYPE = "SDL2"

# Addresses
ADDR_LIVES = 0xC699
ADDR_PLAYER_X = 0xC1A0
ADDR_PLAYER_Y = 0xC1A2

def read_score_bcd(memory):
    """Lee el score en formato BCD."""
    score_bytes = [
        memory[0xC601],
        memory[0xC602],
        memory[0xC603],
    ]
    
    score = 0
    for byte_val in score_bytes:
        high = (byte_val >> 4) & 0x0F
        low = byte_val & 0x0F
        score = score * 100 + high * 10 + low
    
    return score

def main():
    print("="*60)
    print("VERIFICACIÓN DE FIXES - SNOW BROS RL")
    print("="*60)
    print("\n📋 Verificando:")
    print("  1. Game Over cuando lives=255 (display vacío)")
    print("  2. Puntos solo cuando score aumenta\n")
    
    pyboy = PyBoy(ROM_PATH, window=WINDOW_TYPE)
    pyboy.set_emulation_speed(1)
    
    previous_score = 0
    previous_lives = 3
    
    while True:
        pyboy.tick()
        
        if pyboy.frame_count % 30 == 0:  # Cada ~0.5 segundos
            lives = pyboy.memory[ADDR_LIVES]
            current_score = read_score_bcd(pyboy.memory)
            px = pyboy.memory[ADDR_PLAYER_X]
            py = pyboy.memory[ADDR_PLAYER_Y]
            
            # Mostrar estado general
            print(f"\n[Estado] Lives: {lives:3d} | Score: {current_score:8d} | Pos: ({px:3d}, {py:3d})")
            
            # Verificar cambios de score
            if current_score > previous_score:
                gain = current_score - previous_score
                print(f"  ✅ SCORE AUMENTÓ: +{gain} puntos")
            elif current_score < previous_score:
                print(f"  ⚠️  Score disminuyó (posible reset)")
            
            # Verificar cambios de vidas
            if lives < previous_lives and lives >= 0 and lives <= 3:
                print(f"  💔 VIDA PERDIDA: {previous_lives} -> {lives}")
            
            # Detectar posible Game Over
            if lives == 255:
                print(f"  🚨 DISPLAY VACÍO DETECTADO (lives=255) - GAME OVER!")
            elif lives == 0:
                print(f"  ⚠️  Lives=0 (puede ser temporal)")
            
            previous_score = current_score
            if lives in [0, 1, 2, 3]:
                previous_lives = lives
            
        time.sleep(0.001)

if __name__ == "__main__":
    main()
