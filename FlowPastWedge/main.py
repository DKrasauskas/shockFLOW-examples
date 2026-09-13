import shockFLOW.examples as examples
import os



#initializing the freestream mach numbers we want to run the simulation at:
v_inf_x = [1.6] #, 1.2, 1.4, 1.6, 1.8]

#initializing the names of the output files
names = ["M15.mp4"] #,   "M12.mp4", "M14.mp4", "M16.mp4", "M18.mp4"]#, "M20.mp4", "M22.mp4", "M24.mp4"]

current_path = os.getcwd()
for i, v in enumerate(v_inf_x):

    examples.run_cylinder_example3(
        dimx = 4000, dimy = 2000,
        screen_x=2000, screen_y=1000,
        radius = 100,
        simulation_end=200,
        config = "config_wedge.yaml",
        settings = "settings_wedge.yaml",
        working_dir=current_path + "/FlowPastWedge",
        gradient_name=names[i],
        v_inf_x = v
    )

#shock attachement occurs at ~ 23 degrees => height / width = 0.84