#!/usr/bin/env python3

import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pylab import *
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np



FCST_VAR = sys.argv[1]

#FCST_VAR = 'T2'
#cnt_file = '/d1/personal/kalb/ACOM/MET_output/StatAnalysis/surface/WRF_MADIS_surface_2022072000_2022072023_separate_stations_CNT.stat'
#mpr_file = '/d1/personal/kalb/ACOM/MET_output/StatAnalysis/surface/WRF_MADIS_surface_2022072000_2022072023_AllVars_FULL_MPR.stat'
#plot_output_dir = '/d1/personal/kalb/ACOM/MET_output/plots/surface_maps'

cnt_file = os.environ['MAP_CNT_FILE']
mpr_file = os.environ['MAP_MPR_FILE']
plot_output_dir = os.environ['MAP_OUTPUT_DIR']


STAT = 'ME'

# Read in the CNT Data
cnt_data_in = pd.read_csv(cnt_file,sep=r'\s+')

# Read in the MPR file to get the lats/lons
mpr_data_in = pd.read_csv(mpr_file,sep=r'\s+')


# Sort based on variable
cnt_data = cnt_data_in.loc[cnt_data_in['FCST_VAR'].eq(FCST_VAR)]
mpr_data = mpr_data_in.loc[mpr_data_in['FCST_VAR'].eq(FCST_VAR)]

# Find the unique MPR sites
mpr_data_unique = mpr_data.drop_duplicates(subset=['OBS_SID'])

# Match up the lat/lon
alldata = cnt_data.merge(mpr_data_unique[['OBS_SID','OBS_LAT','OBS_LON']],left_on='VX_MASK',right_on='OBS_SID')

# Pull out some data for plotting
station_id = alldata['OBS_SID']
bias = alldata[STAT]
plat = alldata['OBS_LAT']
plon = alldata['OBS_LON']


# Pull out some data for the title
var_units = alldata['FCST_UNITS'].iloc[0]
start_dates = pd.to_datetime(alldata['FCST_VALID_BEG'],format='%Y%m%d_%H%M%S')
end_dates = pd.to_datetime(alldata['FCST_VALID_END'],format='%Y%m%d_%H%M%S')
min_date = start_dates.min()
max_date = end_dates.max()


# Make plotting output directory if it does not exist
if not os.path.isdir(plot_output_dir):
    os.makedirs(plot_output_dir)


# Scaling for plot size
minbias = np.min(bias)
maxbias = np.max(bias)
scaledbias = (bias - minbias) / (maxbias - minbias)
scaledbias = scaledbias*100.

# Make a graphic
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')

cmap = plt.get_cmap('gist_rainbow_r')
#cax = plt.scatter(plon,plat,c=bias, s=(bias+abs(np.min(bias)))*10, vmin=min(bias), vmax=max(bias),cmap=cmap,edgecolors='black')
cax = plt.scatter(plon,plat,c=bias, s=scaledbias, vmin=min(bias), vmax=max(bias),cmap=cmap,edgecolors='black')
cbar = plt.colorbar(cax, shrink=.78, pad=0.02)
cbar.ax.set_title(var_units)
plt.title(FCST_VAR+' '+STAT+' Valid '+min_date.strftime('%Y/%m/%d %H%M')+' to '+max_date.strftime('%Y/%m/%d %H%M'))
plt.tight_layout()


plt.savefig(os.path.join(plot_output_dir,FCST_VAR+'_'+STAT+'_map_'+min_date.strftime('%Y%m%d%H%M%S')+'_'+max_date.strftime('%Y%m%d%H%M%S')+'.png'))
