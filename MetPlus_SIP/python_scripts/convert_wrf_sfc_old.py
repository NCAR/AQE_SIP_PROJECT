#!/usr/bin/env python3

import sys
import netCDF4
import numpy as np
from datetime import datetime
from metpy.calc import dewpoint_from_specific_humidity,relative_humidity_from_specific_humidity
from metpy.units import units


# Date Formats
FILE_DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
MET_DATE_FORMAT ='%Y%m%d_%H%M%S'

# Get Arguments
if len(sys.argv) != 3:
    print("ERROR: Must supply input file and variable to script")
    sys.exit(1)

# read input data
infile = sys.argv[1]
var = sys.argv[2]

# Read the input file
try:
    ncin = netCDF4.Dataset(infile)

    # Read and setup the times
    valid_dt = datetime.strptime(ncin.variables['Times'][:].tobytes().decode(),FILE_DATE_FORMAT)

    # Read latitude and longitude
    lat = ncin.variables['XLAT'][:]
    lon = ncin.variables['XLONG'][:]

except:
    print("Trouble reading input WRF file")
    sys.exit(1)

# Read desired variable
# Temperature
if var == 'T2':
    outvar = ncin.variables[var][:]
    var_name = var
    var_units = ncin.variables[var].units
    var_long_name = 'Temperature'
    var_lvl = 'Z2'

# Dew Point Temperature Calculation
elif var == 'DPT':
    # Read in Q2 and Surface Pressure
    Q2 = ncin.variables['Q2'][:]
    Q2_units = ncin.variables['Q2'].units
    psfc = ncin.variables['PSFC'][:]
    psfc_units = ncin.variables['PSFC'].units
    temperature = ncin.variables['T2'][:]
    temperature_units = ncin.variables['T2'].units

    # Assign units
    Q2 = units.Quantity(Q2,Q2_units)
    psfc = units.Quantity(psfc,psfc_units)
    temperature = units.Quantity(temperature,temperature_units)

    # Convert Q2 to Dewpoint
    dewpt_calc_C = dewpoint_from_specific_humidity(psfc, temperature, Q2)
    dewpt_calc = dewpt_calc_C.to(units.K)

    # Set up variable and attributes
    outvar = dewpt_calc.magnitude
    var_name = 'DPT'
    var_units = 'K'
    var_long_name = 'Dew Point Temperature'
    var_lvl = 'Z2'

# U-Wind
elif var == 'U10':
    outvar = ncin.variables[var][:]
    var_name = 'U'
    var_units = ncin.variables[var].units
    var_long_name = 'U Wind'
    var_lvl = 'Z10'

# V-Wind
elif var == 'V10':
    outvar = ncin.variables[var][:]
    var_name = 'V'
    var_units = ncin.variables[var].units
    var_long_name = 'V wind'
    var_lvl = 'Z10'

# Relative Humidity Calculation
elif var == 'RH':
    # Read in Q2, surface pressure, and temperature
    Q2 = ncin.variables['Q2'][:]
    Q2_units = ncin.variables['Q2'].units
    psfc = ncin.variables['PSFC'][:]
    psfc_units = ncin.variables['PSFC'].units
    T2 = ncin.variables['T2'][:]
    T2_units = ncin.variables['T2'].units

    # Assign units
    Q2 = units.Quantity(Q2,Q2_units)
    psfc = units.Quantity(psfc,psfc_units)
    T2 = units.Quantity(T2,T2_units)

    # Calculate RH
    rh_calc = relative_humidity_from_specific_humidity(psfc, T2, Q2).to('percent')

    # Set up variable and attributes
    outvar = rh_calc.magnitude
    var_name = 'RH'
    var_units = '%'
    var_long_name = 'Relative Humidity'
    var_lvl = 'Z2'

elif var == 'PSFC':
    outvar = ncin.variables[var][:]
    var_name = var
    var_units = ncin.variables[var].units
    var_long_name = 'Surface Pressure'
    var_lvl = 'Z0'

elif var == 'WIND':
    uwind = ncin.variables['U10'][:]
    uwind_units = ncin.variables['U10'][:].units
    vwind = ncin.variables['V10'][:]
    vwind_units = ncin.variables['V10'][:].units

    # Add units
    uwind = units.Quantity(uwind,uwind_units)
    vwind = units.Quantity(vwind,vwind_units)

    # Compute Wind speed
    wspeed_calc = wind_speed(uwind,vwind)

    # Set up variable and attributes
    outvar = wspeed_calc.magnitude
    var_name = 'WIND'
    var_units = 'm_s-1'
    var_long_name = 'Wind Speed'
    var_lvl = 'Z10'

else:
    # No support for selected variable
    # Error with message
    raise NameError('Variable '+ var+' not currently supported')
    print('Use T2, U10, V10, DPT, RH, PSFC, or WIND as the input variable')
    sys.exit(1)


# Set up variable to output to MET
outvar = np.squeeze(outvar)
met_data = outvar[::-1]

# Some grid dimensions that need to be calculated
d_km = float(ncin.getncattr('DX')) / 1000 

# Set up attributes
attrs = {
   'valid': valid_dt.strftime(MET_DATE_FORMAT),
   'init': valid_dt.strftime(MET_DATE_FORMAT),
   'lead': '000000',
   'accum': '000000',
   'name': var_name,
   'long_name': var_long_name,
   'level': var_lvl,
   'units': var_units,
   'grid': {
       'type': ncin.getncattr('MAP_PROJ_CHAR'),
       'hemisphere': 'N' if float(ncin.getncattr('POLE_LAT')) > 0 else 'S',
       'name': var_name,
       'nx': int(ncin.dimensions['west_east'].size),
       'ny': int(ncin.dimensions['south_north'].size),
       'lat_pin': float(ncin.getncattr('CEN_LAT')),
       'lon_pin': float(ncin.getncattr('CEN_LON')),
# CDPHE domain
#       'x_pin': float(109),
#       'y_pin': float(88),
#ACOM wrfmet files
       'x_pin': float(87.5),
       'y_pin': float(77),
       'lon_orient': float(ncin.getncattr('STAND_LON')),
       'd_km': d_km,
       'r_km': 6371.2,
       'scale_lat_1': float(ncin.getncattr('TRUELAT1')),
       'scale_lat_2': float(ncin.getncattr('TRUELAT2')),
   }
}

# Close netCDF file
ncin.close()

print("Attributes: " + repr(attrs))
