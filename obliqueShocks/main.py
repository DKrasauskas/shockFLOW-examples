import shockFLOW.examples as examples
import os

v_inf_x = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
names = ["M10.mp4",   "M12.mp4", "M14.mp4", "M16.mp4", "M18.mp4", "M20.mp4", "M22.mp4"]

current_path = os.getcwd()
for i, v in enumerate(v_inf_x):

    examples.run_wedge_example(
        dimx = 4000, dimy = 2000,
        screen_x=2000, screen_y=1000,
        wedge_height=200, wedge_width=200,
        simulation_end=300,
        config = "config_wedge.yaml",
        settings = "settings_wedge.yaml",
        working_dir=current_path + "/FlowPastWedge",
        gradient_name=names[i],
        v_inf_x = v
    )

#shock attachement occurs at ~ 23 degrees => height / width = 0.84