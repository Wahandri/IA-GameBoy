import sys
import random
import time
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent

# --- CONFIGURACIÓN ---
ROM_PATH = "roms/super-mario-land.gb"
EMULATION_SPEED = 0  # Velocidad máxima para aprendizaje
WINDOW_TYPE = "SDL2" 

# --- DIRECCIONES DE MEMORIA (SUPER MARIO LAND) ---
ADDR_SCROLL_X = 0xC0A1       # Posición de cámara
ADDR_SCROLL_PAGE = 0xC0A2    # Multiplicador de página para distancia total
ADDR_STATUS = 0xFF99          # 00=Vivo, 01=Muriendo
ADDR_LIVES = 0xDA15          # Vidas reales
ADDR_SCORE_BCD = range(0xC0A0, 0xC0A3) # Marcador en formato BCD

class MarioAgent:
    def __init__(self, rom_path):
        print(f"--- INICIANDO MARIO PRO AGENT ---")
        self.pyboy = PyBoy(rom_path, window=WINDOW_TYPE)
        self.pyboy.set_emulation_speed(EMULATION_SPEED)
        self.memory = self.pyboy.memory
        
        # Estado de la IA
        self.max_distance = 0
        self.total_reward = 0
        self.stuck_frames = 0
        self.last_x = 0
        self.previous_score = 0
        
        # Q-Learning Parameters
        self.q_table = {} # state: [q_values]
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.005
        self.alpha = 0.2 # Learning Rate
        self.gamma = 0.9 # Discount Factor
        self.generation = 1
        
        # Acciones: Solo las necesarias para ganar (sin 'Izquierda')
        self.actions = [
            [WindowEvent.PRESS_ARROW_RIGHT],
            [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_B], # Sprint
            [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_A], # Salto largo
            [WindowEvent.PRESS_BUTTON_A],                                # Salto alto
            [WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.PRESS_BUTTON_A, WindowEvent.PRESS_BUTTON_B],
            [] # Idle
        ]
        self.event_map = {getattr(WindowEvent, x): x for x in dir(WindowEvent) if x.startswith("PRESS_")}

    def get_state(self):
        """Define el estado como la posición global discretizada."""
        return self.get_global_x() // 10

    def choose_action(self, state):
        """Estrategia Epsilon-Greedy."""
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)

        if random.random() < self.epsilon:
            return random.randint(0, len(self.actions) - 1)
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        """Actualiza Q-Value usando la ecuación de Bellman."""
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * len(self.actions)

        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        # Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s')) - Q(s,a))
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value

    def get_score(self):
        """Lee el score BCD y lo convierte a entero para recompensas."""
        score = 0
        for addr in ADDR_SCORE_BCD:
            val = self.memory[addr]
            score = score * 100 + ((val >> 4) * 10) + (val & 0x0F)
        return score

    def get_global_x(self):
        """Calcula la distancia real de Mario en el nivel completo."""
        return self.memory[ADDR_SCROLL_X] + (self.memory[ADDR_SCROLL_PAGE] * 256)

    def step(self, action_idx):
        selected = self.actions[action_idx]
        for key in selected: self.pyboy.send_input(key)
        
        for _ in range(12): self.pyboy.tick() # Avance físico
            
        for key in selected:
            if key in self.event_map:
                rel = getattr(WindowEvent, self.event_map[key].replace("PRESS", "RELEASE"))
                self.pyboy.send_input(rel)
        self.pyboy.tick()

        # --- SISTEMA DE RECOMPENSAS (Q-LEARNING) ---
        curr_x = self.get_global_x()
        curr_score = self.get_score()
        is_dead = (self.memory[ADDR_STATUS] == 1)
        reward = 0
        
        # 1. Recompensa por Progreso
        if curr_x > self.last_x:
            reward += (curr_x - self.last_x) * 15
            self.stuck_frames = 0
        else:
            self.stuck_frames += 1
            
        # Actualizar max distance para registro
        if curr_x > self.max_distance:
            self.max_distance = curr_x

        # 2. Recompensa por Puntos
        if curr_score > self.previous_score:
            print(f"  [+] PUNTOS: {curr_score - self.previous_score}")
            reward += 50
            self.previous_score = curr_score

        # 3. Penalización por Muerte
        if is_dead:
            reward -= 500
            print(f"  [💀] MUERTE DETECTADA")
            
        # 4. Penalización por Stuck (se maneja el reset fuera, pero aquí el reward)
        if self.stuck_frames > 100:
            reward -= 10

        self.total_reward += reward
        self.last_x = curr_x
        
        next_state = self.get_state()
        return next_state, reward, is_dead

    def run(self):
        self.start_sequence()
        step = 0
        
        while True:
            state = self.get_state()
            action_idx = self.choose_action(state)
            
            next_state, reward, dead = self.step(action_idx)
            
            self.update_q_table(state, action_idx, reward, next_state)
            
            if step % 30 == 0:
                print(f"Gen: {self.generation} | Paso: {step} | Epsilon: {self.epsilon:.3f} | Dist: {self.last_x} | Reward: {self.total_reward:.1f}")

            # REINICIO: Si muere o se queda 100 pasos quieto
            if dead or self.stuck_frames > 100:
                print(f"\n--- [RESET] Gen {self.generation} terminada. Record: {self.max_distance} ---")
                self.reset_agent()
                step = 0
            step += 1

    def start_sequence(self):
        """Pulsar Start para entrar al nivel 1-1."""
        print("--- ESPERANDO LOGOS (3s) ---")
        for _ in range(180): self.pyboy.tick()
        
        print("--- PULSANDO START ---")
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        for _ in range(10): self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        for _ in range(60): self.pyboy.tick()

    def reset_agent(self):
        """Reinicia el juego usando Soft Reset (A+B+Start+Select)."""
        print("--- SOFT RESET (A+B+Start+Select) ---")
        # Soft Reset: A + B + Start + Select
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_B)
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_SELECT)
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        
        for _ in range(10): self.pyboy.tick()
        
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_B)
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_SELECT)
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        # Esperar a que reinicie
        for _ in range(60): self.pyboy.tick()
        
        # Reiniciar estado interno
        self.max_distance = 0
        self.total_reward = 0
        self.stuck_frames = 0
        self.last_x = 0
        self.previous_score = 0
        
        # Decaimiento de Epsilon y aumento de generación
        if self.epsilon > self.epsilon_min:
            self.epsilon -= self.epsilon_decay
        self.generation += 1
        
        self.start_sequence()

if __name__ == "__main__":
    agent = MarioAgent(ROM_PATH)
    agent.run()