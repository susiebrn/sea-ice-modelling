import os
from cdo import Cdo

cdo = Cdo()

def compute_siv_sh(siconc_path, sithick_path, output_path_prefix):
    """
    Compute sea ice concentration, thickness and volume for Southern Hemisphere using CDO.
    
    Parameters:
    - siconc_path (str): Path to sea ice concentration file (siconc).
    - sithick_path (str): Path to sea ice thickness file (sithick).
    - output_path_prefix (str): Prefix for the output files (without extension).
    
    Output files:
    - {prefix}_siconc_sh.nc: Sea ice concentration restricted to Southern Hemisphere.
    - {prefix}_sithick_sh.nc: Sea ice thickness restricted to Southern Hemisphere.
    - {prefix}_siv_sh.nc: Sea ice volume file.
    """

    # Ensure output directory exists
    output_path = os.path.dirname(output_path_prefix)

    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path)

    # Step 1: Create grid area file
    grid_area = f"{output_path_prefix}_gridarea.nc"
    cdo.gridarea(input=siconc_path, output=grid_area)

    # Step 2: Restrict to Southern Hemisphere (e.g., -90 to -50 latitude)
    grid_area_sh = f"{output_path_prefix}_gridarea_sh.nc"
    cdo.sellonlatbox('-180,180,-90,-50', input=grid_area, output=grid_area_sh)

    siconc_sh = f"{output_path_prefix}_siconc_sh.nc"
    sithick_sh = f"{output_path_prefix}_sithick_sh.nc"

    cdo.sellonlatbox('-180,180,-90,-50', input=siconc_path, output=siconc_sh)
    cdo.sellonlatbox('-180,180,-90,-50', input=sithick_path, output=sithick_sh)

    # Scale siconc to fraction (0–1)
    siconc_frac = f"{output_path_prefix}_siconc_frac.nc"
    cdo.divc(100, input=siconc_sh, output=siconc_frac)

    # Step 3: Multiply concentration, thickness, and area
    siv_temp = f"{output_path_prefix}_siv_tmp.nc"
    cdo.mul(input=f"{siconc_sh} {sithick_sh}", output=siv_temp)  # siconc * sithick
    siv_file = f"{output_path_prefix}_siv_sh.nc"
    cdo.mul(input=f"{siv_temp} {grid_area_sh}", output=siv_file)  # * gridarea

    # Step 4: Rename and add metadata
    final_output = f"{output_path_prefix}_siv_sh1.nc"     
    cdo.copy(
    input=(
        f"-setattribute,SIA_SH@units='m^3' "
        f"-setattribute,SIA_SH@long_name='Sea Ice Volume Southern Hemisphere' "
        f"-chname,siconc,SIV_SH {output_path_prefix}_siv_sh.nc"
    ),
    output=final_output
    )


    for f in [grid_area, grid_area_sh, siv_temp, siv_file, siconc_frac]:
        if os.path.exists(f):
            os.remove(f)

    print(f"Sea ice volume saved to {final_output}")