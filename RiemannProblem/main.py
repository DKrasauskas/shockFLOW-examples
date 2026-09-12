import shockFLOW.utils as helpers
import shockFLOW.solver as flow
from shockFLOW.utils import hdf5_read_midline
import shockFLOW.analytical as al
import matplotlib.pyplot as plt
import os
import numpy as np

module_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))


#create directories for Videos and Logs
os.makedirs("Videos", exist_ok=True)
os.makedirs("Logs", exist_ok=True)
current_dir = os.getcwd()



#Configuration and settings file paths
config = "riemann.yaml"
settings = "settings.yaml"

#Simulation Domain
dimx = 20000
dimy = 300
helpers.set_simulation_domain(config, dimx, dimy, 1)


#Change the EXT event so that the simulation runs for 300us
helpers.set_ext_event_times(config, 300)  

#for relatively weak shocks, debug can be disabled
helpers.set_debug_mode(settings, False)

#set video output dir
helpers.set_ffmpeg_output_path(settings, current_dir + "/")

#set log output dir
helpers.set_logging_folder(settings, current_dir + "/Logs")

#set hdf5 output path
helpers.set_hdf5_output_path(config, current_dir + "/")


#run the simulation
flow.custom(settings, config, current_dir)


#read midline of the exported simulation results
data = hdf5_read_midline(os.getcwd() + "/200", axis="x")



#Get the analytical solutions for pressure, density and temperature
x_a, p_a, rho_a, temp_a = al.get_analytical_solution(x0=0, time=200e-6)



#plotting the results
plt.style.use("seaborn-v0_8-whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
fig.suptitle("Riemann Problem — Simulation vs. Analytical Solution (t = 200 μs)",
                fontsize=14, fontweight="bold")

sim_style = dict(color="tab:blue", lw=1.5, label="Simulation")
ana_style = dict(color="tab:red", lw=1.5, ls="--", label="Analytical")

plot_specs = [
    (axes[0, 0], "density",     rho_a,  r"Density Ratio $\rho / \rho_0$"),
    (axes[0, 1], "pressure",    p_a,    r"Pressure Ratio $p / p_0$"),
    (axes[1, 0], "temperature", temp_a, r"Temperature Ratio $T / T_0$"),
    (axes[1, 1], "vx",          None,   r"Velocity $v_x$ [m/s]"),
]

for ax, key, analytical, ylabel in plot_specs:
    ax.plot(data["coord"], data[key], **sim_style)
    if analytical is not None:
        ax.plot(x_a, analytical, **ana_style)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlim(-10, 10)
    ax.legend(fontsize=9, frameon=True)
    ax.tick_params(labelsize=9)

axes[1, 0].set_xlabel("x [mm]", fontsize=10)
axes[1, 1].set_xlabel("x [mm]", fontsize=10)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(os.path.join(os.getcwd(), "Videos", "riemann_comparison.png"), dpi=200)
plt.show()