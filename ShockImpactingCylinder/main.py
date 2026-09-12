import shockFLOW.examples as examples
import shockFLOW.nozzle   as nc
import shockFLOW.utils    as helpers
import shockFLOW.solver   as flow
import os


module_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#create directories for Videos and Logs
os.makedirs("Videos", exist_ok=True)
os.makedirs("Logs", exist_ok=True)

path_run = os.getcwd()
output_dir = os.getcwd() + "/Videos/"

dimx = 4000
dimy = 2000
radius = 100
exit_time = 300 #us

#create the binary mask for a rectangle BC
nc.create_sphere_bc(dimx, dimy, os.getcwd() + "/", radius)

config = "impact.yaml"
settings = "settings.yaml"


helpers.set_boundary_files(config, path_run + "/sphere.bin", path_run + "/spheren.bin")
helpers.set_simulation_domain(config, dimx, dimy, 1)
helpers.set_logging_folder(settings, path_run + "/Logs")
helpers.set_ext_event_times(config, exit_time)
helpers.set_ffmpeg_output_path(settings, output_dir)
print("Starting Simulation", flush =True)
flow.custom(settings, config, path_run)