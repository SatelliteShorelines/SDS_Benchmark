# import packages and setup ssl context
import os
import ssl
import urllib3
from bs4 import BeautifulSoup
import wget
from netCDF4 import Dataset            
import skimage.transform as transform
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy import stats
import pickle
import warnings

from datetime import datetime, timedelta
import pytz

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
plt.ion()

import geopandas as gpd
import shapely

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

#%% Download DUCK data
 
# folder to save the files in
sitename = 'DUCK'
data_folder = os.path.join('datasets',sitename)
if not os.path.exists(data_folder): os.makedirs(data_folder)
fp_raw = os.path.join(data_folder,'raw')
if not os.path.exists(fp_raw): os.makedirs(fp_raw)
fp_processed = os.path.join(data_folder,'processed')
if not os.path.exists(fp_processed): os.makedirs(fp_processed)

# parse catalog to find all the file names
http = urllib3.PoolManager()
url_catalog = 'https://chlthredds.erdc.dren.mil/thredds/catalog/frf/geomorphology/elevationTransects/survey/data/catalog.html'
response = http.request('GET', url_catalog)
soup = BeautifulSoup(response.data)
# split string
soup_str = soup.text
soup_split = soup_str.split('.nc')
print('Found %d files to download'%len(soup_split))

# download all the files
main_http_server = 'https://chlthredds.erdc.dren.mil/thredds/fileServer/frf/geomorphology/elevationTransects/survey/data/'
print('Downloading %d files'%(len(soup_split)))
for i,text in enumerate(soup_split):
    print('\r%d%%' %int((i+1)/len(soup_split)), end='')
    fn = text[text.find('FRF'):]
    date = fn[-8:]
    if int(date[:4]) < 1984: continue
    url = main_http_server + fn + '.nc'
    
    # download file (try until host responds)
    file = []
    while len(file) == 0:
        file = wget.download(url, out=fp_raw)

#%% Preprocess DUCK data
# format data along selected profiles (which have sufficient data)
# profiles = [1, 46, 91, 137, 183, 229, 274, 320, 366, 411, 457, 558, 594, 640, 686, 731, 
#             777, 823, 869, 914, 927, 951, 960, 1006, 1052, 1097, 1157, 1217, 1277, 1337,65445, 65490]
profiles = [1,1097]
pf_names = [str(_) for _ in profiles]
contour_level = 0.4 # = MHWS in Navd88 https://tidesandcurrents.noaa.gov/datums.html?datum=NAVD88&units=1&epoch=0&id=8651370&name=Duck&state=NC

# read all files and merge them
survey_data = dict([])
filenames = os.listdir(fp_raw)
filenames = [_ for _ in filenames if not _ == '.nc']
for fn in filenames:
    data = Dataset(os.path.join(fp_raw,fn))
    date_str = fn[-11:].split('.nc')[0]
    date = pytz.utc.localize(datetime.strptime(date_str,'%Y%m%d'))
    survey_number = np.array(data.variables['surveyNumber'][:])[0]
    survey_data[str(survey_number)] = dict([])
    survey_data[str(survey_number)]['date'] = date
    survey_data[str(survey_number)]['latitude'] = np.array(data.variables['lat'][:])
    survey_data[str(survey_number)]['longitude'] = np.array(data.variables['lon'][:])
    survey_data[str(survey_number)]['x'] = np.array(data.variables['xFRF'][:])
    survey_data[str(survey_number)]['y'] = np.array(data.variables['yFRF'][:])
    survey_data[str(survey_number)]['elevation'] = np.array(data.variables['elevation'][:])
    survey_data[str(survey_number)]['profile'] = np.array(data.variables['profileNumber'][:])

# format the data by profile and not by date
fp_figs = os.path.join(fp_processed,'figs_topo')
if not os.path.exists(fp_figs): os.makedirs(fp_figs)
topo_profiles = dict([])
for i in range(len(pf_names)):
    topo_profiles[pf_names[i]] = {'dates':[],'chainages':[]}
    fig, ax = plt.subplots(1,1,figsize=(12,8),tight_layout=True)
    ax.grid()
    for n in list(survey_data.keys()):
        survey = survey_data[n]
        idx = np.where(survey['profile'] == profiles[i])[0]
        if len(idx) == 0: 
            continue
        date = survey_data[n]['date']
        chainages = survey['x'][idx]
        elevations = survey['elevation'][idx]
        # sort by chainages
        idx_sorted = np.argsort(chainages)
        chainages = chainages[idx_sorted]
        elevations = elevations[idx_sorted]
        chainages_interp = np.arange(np.min(chainages),np.max(chainages),1)
        elevations_interp = np.interp(chainages_interp,chainages,elevations)
        # use interpolation to extract the chainage at the contour level
        f = interpolate.interp1d(elevations_interp, chainages_interp, bounds_error=False)
        chainage_contour_level = float(f(contour_level))            
        topo_profiles[pf_names[i]]['chainages'].append(chainage_contour_level)
        topo_profiles[pf_names[i]]['dates'].append(date)        
        ax.plot(chainages,elevations,'-',c='0.3',lw=1)
        ax.plot(chainage_contour_level,contour_level,'r.')

    # convert to np.array
    topo_profiles[pf_names[i]]['chainages'] = np.array(topo_profiles[pf_names[i]]['chainages'])
    if len(topo_profiles[pf_names[i]]['dates']) > 0:
        ax.set(title = 'Transect %s  - %d surveys'%(pf_names[i],len(topo_profiles[pf_names[i]]['dates'])),
               xlabel='chainage [m]', ylabel='elevation [m]', ylim=[-5,5],
               xlim=[np.nanmin(topo_profiles[pf_names[i]]['chainages'])-20,
                     np.nanmax(topo_profiles[pf_names[i]]['chainages'])+20])    
        # fig.savefig(os.path.join(fp_figs, 'transect_%s.jpg'%pf_names[i]), dpi=100)
    else:
        topo_profiles.pop(pf_names[i])
        plt.close(fig)
    
# save survey data
# with open(os.path.join(fp_processed, 'DUCK_groundtruth' + '.pkl'), 'wb') as f:
#     pickle.dump(topo_profiles, f)


#%% Generate DUCK transects

counter = 0
for i in range(len(pf_names)):
    for n in list(survey_data.keys()):
        survey = survey_data[n]
        idx = np.where(survey['profile'] == profiles[i])[0]
        if len(idx) == 0: 
            continue
        chainages = survey['x'][idx]
        latitudes =  survey['latitude'][idx]
        longitudes =  survey['longitude'][idx]
        idx_sorted = np.argsort(chainages)
        latitudes = latitudes[idx_sorted]
        longitudes = longitudes[idx_sorted]
        # create transect
        coords = np.array([[longitudes[0],latitudes[0]],
                          [longitudes[-1],latitudes[-1]]])
        line = shapely.geometry.LineString(coords)
        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(line))
        gdf.index = [i]
        gdf.at[i,'name'] = 'PF%d'%profiles[i]
        # store into geodataframe
        if counter == 0:
            gdf_all = gdf
        else:
            gdf_all = gdf_all.append(gdf)
        counter = counter + 1
        break
    
gdf_all = gdf_all.set_crs('epsg:4326')
# save GEOJSON layer to file
gdf_all.to_file('transects.geojson',  driver='GeoJSON', encoding='utf-8')

#%% Preprocess TRUCKVERT data

# folder to save the files in
sitename = 'TRUCVERT'
contour_level = 0
data_folder = os.path.join('datasets',sitename)
if not os.path.exists(data_folder): os.makedirs(data_folder)
fp_raw = os.path.join(data_folder,'raw')
if not os.path.exists(fp_raw): os.makedirs(fp_raw)
fp_figs = os.path.join(data_folder,'figs_dem')
if not os.path.exists(fp_figs): os.makedirs(fp_figs)

# read all files and merge them
survey_data = dict([])
filenames = os.listdir(fp_raw)
filenames = [_ for _ in filenames if 'Monitoring' in _]
# load Grid.nc file
grid = Dataset(os.path.join(fp_raw,'Grids.nc'))
grid_data = dict([])
grid_data['lat'] = np.array(grid.variables['latg'][:])
grid_data['lon'] = np.array(grid.variables['long'][:])
grid_data['x'] = np.array(grid.variables['xlg'][:])
grid_data['y'] = np.array(grid.variables['ylg'][:])
for fn in filenames:
    data = Dataset(os.path.join(fp_raw,fn))
    date_str = fn[-13:].split('.nc')[0]
    date = pytz.utc.localize(datetime.strptime(date_str,'%Y-%m-%d'))
    survey_data[date_str] = dict([])
    survey_data[date_str]['date'] = date
    elevation = np.array(data.variables['zg'][:])
    elevation[elevation < -100] = np.nan
    survey_data[date_str]['elevation'] = elevation

    # plt.figure()
    # plt.axis('equal')
    # plt.grid(which='major',ls=':',c='0.5')
    # plt.scatter(grid_data['x'],grid_data['y'],c=survey_data[date_str]['elevation'])
    # plt.title(date_str)
    # plt.savefig(os.path.join(fp_figs,'survey_%s.jpg'%date_str))
    # plt.close(plt.gcf())

fp_figs = os.path.join(data_folder,'figs_topo')
if not os.path.exists(fp_figs): os.makedirs(fp_figs)
topo_profiles = dict([])
pf_names = [str(int(grid_data['y'][0,i])) for i in range(len(grid_data['y']))]
n_surveys = np.zeros(len(pf_names))
for i in range(len(pf_names)):
    topo_profiles[pf_names[i]] = {'dates':[],'chainages':[]}
    # fig, ax = plt.subplots(1,1,figsize=(12,8),tight_layout=True)
    # ax.grid()
    for n in list(survey_data.keys()):
        survey = survey_data[n]
        date = survey_data[n]['date']
        chainages = grid_data['x'][:,i]
        elevations = survey['elevation'][:,i]
        # remove nans
        idx_nan = np.isnan(elevations)
        # if less than 5 survey points along the transect, skip it
        if len(elevations) - sum(idx_nan) <= 5: continue
        chainages = chainages[~idx_nan]
        elevations = elevations[~idx_nan]
        # use interpolation to extract the chainage at the contour level
        f = interpolate.interp1d(elevations, chainages, bounds_error=False)
        chainage_contour_level = float(f(contour_level))            
        topo_profiles[pf_names[i]]['chainages'].append(chainage_contour_level)
        topo_profiles[pf_names[i]]['dates'].append(date)  
        
        # ax.plot(chainages,elevations,'-',c='0.6',lw=1)
        # ax.plot(chainage_contour_level,contour_level,'r.')

    # convert to np.array
    topo_profiles[pf_names[i]]['chainages'] = np.array(topo_profiles[pf_names[i]]['chainages'])
    n_surveys[i] = len(topo_profiles[pf_names[i]]['dates'])
    # if len(topo_profiles[pf_names[i]]['dates']) > 0:
    #     ax.set(title = 'Transect %s  - %d surveys'%(pf_names[i],len(topo_profiles[pf_names[i]]['dates'])),
    #            xlabel='chainage [m]', ylabel='elevation [m]', ylim=[-5,5],
    #            xlim=[np.nanmin(topo_profiles[pf_names[i]]['chainages'])-20,
    #                  np.nanmax(topo_profiles[pf_names[i]]['chainages'])+20])    
    #     fig.savefig(os.path.join(fp_figs, 'transect_%s.jpg'%pf_names[i]), dpi=100)
    #     plt.close(fig)
    # else:
    #     topo_profiles.pop(pf_names[i])
    #     plt.close(fig)
    
# save survey data
with open(os.path.join(data_folder, 'TRUCVERT_groundtruth' + '.pkl'), 'wb') as f:
    pickle.dump(topo_profiles, f)
    
fig, ax = plt.subplots(1,1,figsize=(10,4), tight_layout=True)
ax.grid(which='major', linestyle=':', color='0.5')
ax.bar(x=grid_data['y'][0,:],height=n_surveys,width=20,fc='C0',ec='None',alpha=0.75)
ax.set(xlabel='alongshore distance [m]',ylabel='number of surveys',title='Survey density')

#%% Generate TRUCVERT transects

counter = 0
for i in range(len(pf_names)):
 
    latitudes =  grid_data['lat'][:,i]
    longitudes =  grid_data['lon'][:,i]
    chainages = grid_data['x'][:,i]
    idx_sorted = np.argsort(chainages)
    latitudes = latitudes[idx_sorted]
    longitudes = longitudes[idx_sorted]
    # create transect
    coords = np.array([[longitudes[0],latitudes[0]],
                      [longitudes[-1],latitudes[-1]]])
    line = shapely.geometry.LineString(coords)
    gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(line))
    gdf.index = [i]
    gdf.at[i,'name'] = 'PF%s'%pf_names[i]
    # store into geodataframe
    if counter == 0:
        gdf_all = gdf
    else:
        gdf_all = gdf_all.append(gdf)
    counter = counter + 1
    
gdf_all = gdf_all.set_crs('epsg:4326')
# save GEOJSON layer to file
gdf_all.to_file('transects.geojson',  driver='GeoJSON', encoding='utf-8')


