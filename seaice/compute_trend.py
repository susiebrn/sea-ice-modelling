import numpy as np
import xarray as xr

def compute_trend(ds, month, variable='siconc'):
    """
    Compute the linear trend of sea ice concentration over time for each grid cell.

    Parameters:
    - ds (xarray.Dataset): Input dataset containing the variable of interest.
    - month (int): Month to select for trend calculation.
    - variable (str): Name of the variable to compute the trend for (default: 'siconc').

    Returns:
    - xarray.DataArray: DataArray containing the linear trend (slope) for each grid cell

    """

    # Select data for the specified month
    ds_month = ds.sel(time=ds.time.dt.month == month)

    # Extract the years only
    time = ds_month.time.dt.year.values

    # Function to compute slope (trend) at each grid cell
    def linregress_1d(y):
        if np.all(np.isnan(y)):
            return np.nan
        else:
            return np.polyfit(time, y, 1)[0]  # slope only

    # Apply across the 'time' dimension using xarray
    trend = xr.apply_ufunc(
        linregress_1d,
        ds_month[variable],
        input_core_dims=[['time']],
        vectorize=True,
        dask='parallelized',
        output_dtypes=[float]
    )

    trend.name = f"{variable}_trend"
    trend.attrs['units'] = f"{ds[variable].attrs.get('units', '')}/year"
    trend.attrs['long_name'] = f"Linear trend of {variable} in {month:02d}"

    return trend