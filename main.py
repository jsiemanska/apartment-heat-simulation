import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from models import Room, Apartment

# 1. SIMULATION PARAMETERS
T_HOURS = 24
ht = 0.05
times = np.arange(ht, T_HOURS, ht)
K = 100
dim = 50
hx = dim / K

# 2. LOAD DATA
try:
    with open('temperatures.txt', 'r') as f:
        temperatures_raw = f.read()
except FileNotFoundError:
    print("File 'temperatures.txt' not found. Please make sure it is in the same directory.")
    exit()

rows = temperatures_raw.split(';')
cool_temps = rows[3].split(",")
cold_temps = rows[5].split(",")
very_cold_temps = rows[7].split(",")

# 3. HELPER FUNCTIONS
def create_apartment(heater_type):
    """Creates the apartment geometry. heater_type=1 (under window), heater_type=2 (on wall)."""
    times_len = len(times)
    
    # ROOM 1
    M = K
    N = int(3 * K / 5)
    D = range(int(M / 5), int(2 * M / 5))
    Wi1 = range(int(N * M - 1 - M / 10 - M / 5), int(N * M - 1 - M / 10))
    Wi2 = range(int(N * M - 1 - 4 * M / 5), int(N * M - 1 - 3 * M / 5))
    Wi = np.unique(np.concatenate([Wi1, Wi2]))
    
    G11 = range(int(N * M - 1 - 13 * M / 10), int(N * M - 1 - 11 * M / 10))
    G12 = range(int(N * M - 1 - 9 * M / 5), int(N * M - 1 - 8 * M / 5))
    G1 = np.unique(np.concatenate([G11, G12]))
    
    G21 = [int(N * M / 3 + k * M + 1) for k in range(1, int(N / 3))]
    if heater_type == 1:
        G22 = [int(N * M / 3 + k * M + 1 + (M - 1)) for k in range(1, int(N / 3))]
    else:
        G22 = [int(N * M / 3 + k * M + 1 + (M - 1) - 2) for k in range(1, int(N / 3))]
    G2 = np.unique(np.concatenate([G21, G22]))
    tops = (int(2 * K**2 / 5), int(K**2 - K), int(2 * K**2 / 5 + K - 1), int(K**2 - 1))
    room1 = Room(M, N, Wi, D, tops, G1, G2, times_len)

    # ROOM 2
    M = int(3 * K / 5)
    N = int(2 * K / 5)
    D1 = range(int(N * M - 1 - 2 * M / 3), int(N * M - 1 - M / 3))
    D2 = [int(M * N / 4 + k * M - 1) for k in range(1, int(N / 2) + 1)]
    D = [D1, D2]
    Wi = range(int(M / 3), int(2 * M / 3 - 1))
    G1 = range(int(4 * M / 3), int(5 * M / 3 - 1))
    G2 = [int(N / 4 * M + k * M + 1) for k in range(1, int(N / 2))]
    tops = (0, int(2 / 5 * K * (K - 1) - M), int(3 / 5 * K - 1), int(2 / 5 * K * (K - 1) + 3 / 5 * K - 1 - M))
    room2 = Room(M, N, Wi, D, tops, G1, G2, times_len)

    # ROOM 3
    M = int(2 * K / 5)
    N = int(2 * K / 5)
    D = [int(M * N / 4 + k * M) for k in range(0, int(N / 2))]
    Wi = range(int(M / 4), int(3 * M / 4 - 1))
    G1 = range(int(M / 4 + M), int(3 * M / 4 - 1 + M))
    G2 = [int((N / 4 + 1) * M) - 2 + k * M for k in range(1, int(N / 2))]
    tops = (int(3 / 5 * K), int(2 / 5 * K * (K - 1) + 3 / 5 * K - M - 20), K - 1, int(2 / 5 * K**2 - 1))
    room3 = Room(M, N, Wi, D, tops, G1, G2, times_len)

    return Apartment([room1, room2, room3], K, times_len)

def run_simulation(temps_array, heater_type=1, turn_off_range=None):
    """Runs simulation and returns the Apartment object."""
    apartment = create_apartment(heater_type)
    initial_temp = float(temps_array[0]) + 273.15
    for room in apartment.rooms:
        room.set_initial_windows(initial_temp)

    for t in range(1, len(times)):
        window_temp = float(temps_array[t]) + 273.15
        apartment.update(t, window_temp, hx, ht, heater_type, turn_off_range)
        apartment.merge(t)
        
    return apartment

def export_gif(apt, filename, label):
    print(f"Rendering {filename}...")
    
    # Ustawienia stylu
    plt.style.use('dark_background') # Ciemne tło dodaje profesjonalizmu mapom ciepła
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    
    # Używamy imshow zamiast pcolormesh dla lepszej kontroli nad wygładzaniem (interpolation)
    # Origin='lower' sprawia, że punkt (0,0) jest na dole po lewej
    img = ax.imshow(
        apt.u[0, :].reshape(K, K),
        extent=[0, dim, 0, dim],
        origin='lower',
        cmap='inferno',       # Bardziej 'termiczna' paleta barw
        interpolation='bilinear', # To sprawia, że wykres jest gładki, a nie kanciasty
        vmin=15, vmax=25      # Stały zakres, żeby kolory nie skakały
    )
    
    cbar = fig.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Temperature [°C]', fontsize=10, color='white')
    
    ax.set_xlabel('Width [m]', fontsize=10)
    ax.set_ylabel('Length [m]', fontsize=10)
    
    def update_frame(f_idx):
        # Obliczanie godziny i minuty
        total_hours = f_idx * ht
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        
        # Aktualizacja danych
        img.set_array(apt.u[f_idx, :].reshape(K, K))
        
        # Nowy, ładniejszy tytuł
        ax.set_title(f"Scenario: {label} | Local Time: {time_str}", 
                     fontsize=12, pad=15, color='white', fontweight='bold')
        return img,

    # Tworzenie animacji
    # Zwiększyłem skok klatek do 12 (co 36 minut), żeby pliki nie były za ciężkie,
    # ale możesz to zmienić na mniejszą liczbę dla większej płynności.
    ani = animation.FuncAnimation(fig, update_frame, frames=range(0, len(times), 10), blit=True)
    
    # Zapis
    ani.save(filename, writer="pillow", fps=10)
    plt.close()
    print(f"Saved {filename}")
    
def save_animation(apartment, filename, title_prefix):
    """Renders and saves the GIF animation."""
    print(f"Generating {filename}...")
    X, Y = np.meshgrid(np.linspace(0, 50, K), np.linspace(0, 50, K))
    fig, ax = plt.subplots(figsize=(4, 4))
    pcm = ax.pcolormesh(X, Y, apartment.u[0, :].reshape(K, K), shading='auto')
    colorbar = fig.colorbar(pcm, ax=ax)
    ax.set_title("Heat map evolution")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    def update(frame):
        data = apartment.u[frame, :].reshape(K, K)
        pcm.set_array(data.ravel())
        pcm.set_clim(vmin=15, vmax=25)
        colorbar.update_normal(pcm)
        ax.set_title(f"Outside: {title_prefix}, t = {frame:.2f}")
        return pcm,

    frames = range(0, len(times), 5)
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    ani.save(filename, writer="pillow")
    plt.close()
    print(f"Saved {filename}")

# 4. MAIN PIPELINE
if __name__ == "__main__":
    print("Starting simulations: Heaters under window...")
    apartment_cool_1 = run_simulation(cool_temps, heater_type=1)
    export_gif(apartment_cool_1, "cool_window.gif", "cool")

    apartment_cold_1 = run_simulation(cold_temps, heater_type=1)
    export_gif(apartment_cold_1, "cold_window.gif", "cold")

    apartment_vcold_1 = run_simulation(very_cold_temps, heater_type=1)
    export_gif(apartment_vcold_1, "very_cold_window.gif", "very cold")

    print("\nStarting simulations: Heaters not under window...")
    apartment_cool_2 = run_simulation(cool_temps, heater_type=2)
    export_gif(apartment_cool_2, "cool_wall.gif", "cool")

    apartment_cold_2 = run_simulation(cold_temps, heater_type=2)
    export_gif(apartment_cold_2, "cold_wall.gif", "cold")

    apartment_vcold_2 = run_simulation(very_cold_temps, heater_type=2)
    export_gif(apartment_vcold_2, "very_cold_wall.gif", "very cold")

    print("\nStarting simulations: Saving schedule (turning off 10:00-16:00)...")
    off_schedule = range(200, 320)
    
    powers_normal = []
    powers_schedule = []
    
    for temps in [cool_temps, cold_temps, very_cold_temps]:
        apartment_normal = run_simulation(temps, heater_type=1)
        powers_normal.append(sum(r.power for r in apartment_normal.rooms))
        
        apartment_sched = run_simulation(temps, heater_type=1, turn_off_range=off_schedule)
        powers_schedule.append(sum(r.power for r in apartment_sched.rooms))

    print("\n--- HEAT CONSUMPTION ---")
    print(f"Constant heating: {powers_normal}")
    print(f"With turning off: {powers_schedule}")
    print("Completed successfully!")