## This repository contains examples & tutorials showcasing the use of shockFLOW - a CUDA based 2D  GPU transonic CFD solver.

<table>
  <tr>
     <td>
      <img src="https://github.com/user-attachments/assets/0f6584f5-e654-4f65-a5b7-a867f198f902", width="100% >
        <figcaption align="center"> Family of Shocks at different Mach numbers around a blunt wedge</figcaption>
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/6ff670fa-c848-457b-9ed3-fb09cd18b412" width="100%">
       <figcaption align="center">  Family of Shocks at different Mach numbers around a slim wedge</figcaption>
    </td>
  </tr>
</table>

Currently these examples are available:
## Example List
 
| Function | Boundary | Config / Settings used | Short Description |
|---|---|---|---|
| `run_wedge_example` | None generated (uses bundled wedge boundary) | `config_wedge.yaml` / `settings_wedge.yaml` | Supersonic (Mach 1.8) freestream impinging on a wedge. |
| `optimize_kernel_launch` | None | `optimization_config.yaml` / `optimization_settings.yaml` | Determines the optimal CUDA thread configuration for a given problem size. |
| `run_cylinder_example` | Sphere/cylinder (`nc.create_sphere_bc`) | `config_sphereSF.yaml` / `settings_sphereSF.yaml` | Supersonic freestream impinging on a cylinder. |
| `run_cylinder_example_monatomic` | Sphere/cylinder (`nc.create_sphere_bc`) | `config_sphereSF.yaml` / `settings_sphereSF.yaml` | Same as `run_cylinder_example`, run with the monatomic solver (`flow.customMonatomic`). |
| `run_naca_example` | NACA airfoil (`nc.create_naca_bc`) | `config_sphereSF.yaml` / `settings_sphereSF.yaml` | Supersonic freestream over a NACA airfoil. |
| `run_nozzle_example` | Nozzle (`nc.create_nozzle_bc`) | `config_nozzle.yaml` / `settings_nozzle.yaml` | Flow through a nozzle geometry. |
| `run_rectangle_example2` | Rectangle (`nc.create_rectangle_bc`) | `shock_impact_scenario/impact.yaml` / `settings.yaml` | A density discontinuity (shock) propagates and impacts a rectangle. |
| `run_naca_example2` | NACA airfoil (`nc.create_naca_bc`) | `shock_impact_scenario/impact.yaml` / `settings.yaml` | A density discontinuity (shock) propagates and impacts a NACA airfoil. |
| `run_riemann_example` | None (1D problem) | `riemann.yaml` / `settings.yaml` | 1D Riemann shock-tube problem, plotted against the analytical solution. |

For detailed information on the examples, you can look into the files wthin this repo. These provide direct ways of seeing how each example is set up behind the scenes with corresponding settings and configuration files.
All of these are abstracted within the examples module of shockFLOW, for more details check the Wiki page of this repo. 
For the official repo, see https://github.com/DKrasauskas/shockFLOW



