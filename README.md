# Apartment Heat Distribution Simulation 🌡️🏠

This project is a Python-based numerical simulation of heat flow within a three-room apartment. It uses the **2D Heat Equation** (a partial differential equation) to analyze how temperature evolves over time based on radiator placement and external weather conditions.

## 📝 Overview
The goal of this simulation is to compare different heating strategies to optimize thermal comfort and energy efficiency. The project models:
* **Heat conduction** using the Laplacian operator.
* **Heat loss** through windows based on real-world external temperature data.
* **Radiator placement impact**: Comparing radiators placed under windows versus on internal walls.
* **Energy Saving Analysis**: Evaluating the efficiency of turning off heaters during specific hours (e.g., when away at work).

## 🔬 Mathematical Model
The simulation solves the following PDE using the finite difference method:

$$\frac{\partial u}{\partial t} = \alpha \Delta u + \frac{P}{\rho Ac} \Theta(x, u)$$

Where:
* $u(x, t)$ is the temperature at point $x$ and time $t$.
* $\alpha$ is the thermal diffusivity coefficient.
* $\Theta(x, u)$ is an indicator function for heat sources (radiators).
* Boundary conditions represent insulated walls (Neumann) and heat exchange through windows (Dirichlet).

## 🚀 Features
* **Real Data Integration**: Reads outdoor temperatures from `temperatures.txt`.
* **Dynamic Visualizations**: Generates animated GIFs showing the heat spread across the apartment layout.
* **Comparative Analysis**: Built-in logic to calculate energy consumption (in %) when using a heating schedule versus constant heating.

## 🛠️ Tech Stack
* **Python 3.x**
* **NumPy**: Numerical grid computations.
* **Matplotlib**: Data visualization and GIF animation.

## 📂 Project Structure
* `main.py` – Entry point; handles simulation loops, schedules, and GIF exporting.
* `models.py` – Contains the `Room` and `Apartment` classes, including the core physics engine (Laplacian computation).
* `temperatures.txt` – External temperature datasets for different scenarios (cool, cold, very cold).
* `*.gif` – Pre-generated simulation results.

## 📊 Quick Start
1. **Clone the repository**:
   ```bash
   git clone [https://github.com/your-username/heat-simulation-python.git](https://github.com/your-username/heat-simulation-python.git)
