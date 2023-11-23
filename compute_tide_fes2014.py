# load modules
import os
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import pandas as pd
from netCDF4 import Dataset 

# global tide model
import pyfes
try:
    filepath = r'C:\Users\z3541792\OneDrive - UNSW\Wet Dry Lines Meso Macro Coastlines\Codes\fes2014_tide_model\fes-2.9.1-Source\data\fes2014'
    config_ocean = os.path.join(filepath, 'ocean_tide.ini')
    config_load =  os.path.join(filepath, 'load_tide.ini')
    ocean_tide = pyfes.Handler("ocean", "io", config_ocean)
    load_tide = pyfes.Handler("radial", "io", config_load)
except:
    filepath = r'C:\Users\Kilian\OneDrive - UNSW\fes-2.9.1-Source\data\fes2014'
    config_ocean = os.path.join(filepath, 'ocean_tide_Kilian.ini')
    config_load =  os.path.join(filepath, 'load_tide_Kilian.ini')  
    ocean_tide = pyfes.Handler("ocean", "io", config_ocean)
    load_tide = pyfes.Handler("radial", "io", config_load)

# load lat-lon grid from the tide model
data = Dataset(os.path.join(filepath, 'ocean_tide', 'm2' + '.nc'))
lats = np.array(data.variables['lat'])
lons = np.array(data.variables['lon'])
amplitude = np.array(data.variables['amplitude'])
no_data_value = data.variables['amplitude']._FillValue
mask = amplitude == no_data_value
amplitude[mask] = np.nan
grid_coords = np.stack([lons[np.where(~mask)[1]],lats[np.where(~mask)[0]]],axis=1)

# compute springs tidal range as MHWS-MLWS = 2*(m2 + s2 + k1 + o1)
components = ['m2', 's2', 'k1', 'o1']
amplitude_dict = dict([])
for k,comp in enumerate(components):
    data = Dataset(os.path.join(filepath, 'ocean_tide', comp + '.nc'))
    amplitude = np.array(data.variables['amplitude'])
    amplitude_dict[comp] = amplitude[np.where(~mask)]
    # uncomment for global plot
    # amplitude[mask] = np.nan
    # if k == 0: amplitude_sum = amplitude
    # else: amplitude_sum += amplitude
    print('%s: min:%.2f  max:%.2f'%(comp, np.min(amplitude_dict[comp]), np.max(amplitude_dict[comp])))
    
amplitude_springs = 2*(amplitude_dict['m2']+amplitude_dict['s2']+amplitude_dict['k1']+amplitude_dict['o1'])/100

# plt.figure()
# plt.imshow(amplitude,cmap='jet')

# plt.figure()
# plt.axis('equal')
# plt.scatter(grid_coords[::100,0],grid_coords[::100,1],s=4,c=amplitude_springs[::100],cmap='jet')

## Two functions to compute the tides
def compute_tide(coords,date_range,time_step,ocean_tide,load_tide):
    'compute time-series of water level for a location and dates using a time_step'
    # list of datetimes (every timestep)
    dates = []
    date = date_range[0]
    while date <= date_range[1]:
        dates.append(date)
        date = date + timedelta(seconds=time_step)
    # convert list of datetimes to numpy dates
    dates_np = np.empty((len(dates),), dtype='datetime64[us]')
    for i,date in enumerate(dates):
        dates_np[i] = datetime(date.year,date.month,date.day,date.hour,date.minute,date.second)
    lons = coords[0]*np.ones(len(dates))
    lats = coords[1]*np.ones(len(dates))
    # compute heights for ocean tide and loadings
    ocean_short, ocean_long, min_points = ocean_tide.calculate(lons, lats, dates_np)
    load_short, load_long, min_points = load_tide.calculate(lons, lats, dates_np)
    # sum up all components and convert from cm to m
    tide_level = (ocean_short + ocean_long + load_short + load_long)/100
    
    return dates, tide_level

def compute_tide_dates(coords,dates,ocean_tide,load_tide):
    'compute time-series of water level for a location and dates (using a dates vector)'
    dates_np = np.empty((len(dates),), dtype='datetime64[us]')
    for i,date in enumerate(dates):
        dates_np[i] = datetime(date.year,date.month,date.day,date.hour,date.minute,date.second)
    lons = coords[0]*np.ones(len(dates))
    lats = coords[1]*np.ones(len(dates))
    # compute heights for ocean tide and loadings
    ocean_short, ocean_long, min_points = ocean_tide.calculate(lons, lats, dates_np)
    load_short, load_long, min_points = load_tide.calculate(lons, lats, dates_np)
    # sum up all components and convert from cm to m
    tide_level = (ocean_short + ocean_long + load_short + load_long)/100
    
    return tide_level

# coords = [ 153.55, -28.17]
# coords = [-117.327382, 32.734179]
# coords = [150.1694, -35.8454] # lon lat
# coords = [67.479999  , 23.936958 ]
# coords = [152.496328, -32.449448]
# coords= [150.093459,-36.931599]
# coords= [8.992062,3.949634]

# sitename = 'Egmond'
# coords = [4.615810, 52.581866]

#sitename = 'OceanBeach'
#coords = [-122.511795, 37.763918]

#sitename = 'Narrabeen'
#coords = [151.301454, -33.700754] # NARRABEEN

# sitename = 'Coolangatta'
# coords = [153.519079, -28.166837]

sitename = 'TRUCVERT'
coords = [-1.559603, 44.940671] # TRUCVERT

#sitename = 'TORREYPINES'
#coords = [-117.307391, 32.903347] # TORREYPINES

# coords = [-80.1164087, 26.2656697]# POMPANO BEACH
# coords = [-75.7437636,36.1763438]# DUCK NC
# coords = [44.940671, -1.559603] # TRUCVERT
# coords = [32.903347, -117.307391] # TORREYPINES

centroid = coords
# get the tide levels for the shoreline dates at the centroid
if centroid[0]<0: centroid[0] = centroid[0] + 360 # grid_coords don't have negative longs
# find closest point on global grid (from FES2014)
idx_closest = np.argmin(np.linalg.norm(centroid-grid_coords, axis=1))
centroid_gridded = grid_coords[idx_closest,:]

# plt.plot(centroid[0],centroid[1],'ro',mfc='none')

# plt.plot(centroid_gridded[0],centroid_gridded[1],'mo',mfc='none')

print('MSTR = %.2f m'%amplitude_springs[idx_closest])

dates_all = []
date = datetime(1984,1,1)
while date <= datetime(2025,1,1):
    date += timedelta(seconds=900)
    dates_all.append(date)  

# tides for each image
tides = compute_tide_dates(centroid_gridded, dates_all, ocean_tide, load_tide)

tide_data = {'dates': dates_all, 'tides':tides}
# with open(os.path.join(os.getcwd(), 'tides_1984_2022.pkl'), 'wb') as f:
#     pickle.dump(tide_data, f)
df = pd.DataFrame(tide_data)

# df.to_csv(os.path.join(os.getcwd(),'NARRA_tides.csv'))
# df.to_csv(os.path.join(os.getcwd(),'FL_0006_tides.csv'))
df.to_csv(os.path.join(os.getcwd(),'{}_tides.csv'.format(sitename)))
# df.to_csv(os.path.join(os.getcwd(),'TRUCVERT_tides.csv'))
# df.to_csv(os.path.join(os.getcwd(),'TORREYPINES_tides.csv'))


plt.figure()
plt.plot(dates_all,tides,'-')