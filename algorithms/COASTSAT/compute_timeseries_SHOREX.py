import os
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
plt.ion()
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from scipy import interpolate
from scipy import stats
import pytz
import json 
# load coastsat package located under algorithms/COASTSAT/
from coastsat import SDS_download, SDS_preprocess, SDS_shoreline, SDS_tools, SDS_transects

# filepaths to all the datasets
fp_datasets = os.path.join(os.path.join(os.pardir,os.pardir,'datasets'))
names_datasets = os.listdir(fp_datasets)
names_datasets = [_ for _ in names_datasets if _ not in ['README.md','sites_info.txt']]
print('\nBenchmark datasets available:\n%s'%(names_datasets))
                
# load site info dict if exists or create
fp_info = os.path.join(fp_datasets,'sites_info.txt')
if os.path.exists(fp_info):
    with open(fp_info,'r') as f: sites_info = json.load(f)  
    print('\nLoaded sites_info.txt.')
else:
    sites_info = {'NARRABEEN':{'beach_slope':0.1,'contour_level':0.7,'epsg':28356},
                  'DUCK':{'beach_slope':0.1,'contour_level':0.585,'epsg':32119},
                  'TRUCVERT':{'beach_slope':0.05,'contour_level':1.5,'epsg':32630},
                  'TORREYPINES':{'beach_slope':0.045,'contour_level':0.792,'epsg':26946},
                  'CALAMILLOR':{'beach_slope':0.1,'contour_level':0,'epsg':2062},
                 }
    with open(fp_info,'w') as f: json.dump(sites_info,f,indent=4)
for key in sites_info.keys(): print('%s: %s'%(key,sites_info[key]))

#%% Load all the shapefile into one dictionary compatible with CoastSat functions

# set filepaths
fp_shorex = os.path.join(os.pardir,os.pardir,'submissions','team_SHOREX')
epsgs = {}
for sitename in names_datasets:
    if sitename in ['CALAMILLOR']: continue
    print(sitename)
    # initialise output dict
    output = {'dates':[],'shorelines':[],'satname':[]}
    # read both directories
    fp_sl1 = os.path.join(fp_shorex,sitename,'shorelines')
    fp_sl2 = os.path.join(fp_shorex,sitename,'remaining_shorelines')
    for fp_sl in [fp_sl1,fp_sl2]:
        print(fp_sl.split('\\')[-1])
        for satname in ['L5','L7','L8','L9','S2']:
            if os.path.exists(os.path.join(fp_sl,'%s.shp'%satname)):
                gdf = gpd.read_file(os.path.join(fp_sl,'%s.shp'%satname))
                epsg = gdf.crs.to_epsg()
                print('%s - %d shorelines - epsg %d'%(satname,len(gdf),epsg))
                # add to output dict
                for i in range(len(gdf)):
                    date_str = gdf.at[i,'DATE'] + ' ' + gdf.at[i,'HOUR']
                    date = pytz.utc.localize(datetime.strptime(date_str,'%Y%m%d %H:%M:%S'))
                    sl_coords = np.array(gdf.at[i,'geometry'].coords)
                    output['dates'].append(date)
                    output['shorelines'].append(sl_coords)
                    output['satname'].append(satname)
    # sort by chronological order
    idx_sorted = sorted(range(len(output['dates'])), key=lambda k: output['dates'][k])
    for key in output.keys():
        output[key] = [output[key][_] for _ in idx_sorted]
    # store shorelines 
    with open(os.path.join(fp_shorex, sitename, sitename + '_output' + '.pkl'), 'wb') as f:
        pickle.dump(output,f) 
    # save epsg code
    epsgs[sitename] = epsg

#%% Compute intersections and tidally correct to MSL and MHWS

fp_shorex = os.path.join(os.pardir,os.pardir,'submissions','team_SHOREX')
for sitename in ['NARRABEEN']:#names_datasets:
    if sitename in ['CALAMILLOR']: continue
    print(sitename)
    # load shorelines
    with open(os.path.join(fp_shorex, sitename, sitename + '_output' + '.pkl'), 'rb') as f:
        output = pickle.load(f)
    # load dataset inputs
    data_folder = os.path.join(fp_datasets,sitename)
    inputs = {}
    inputs['filepath'] = os.path.join(fp_shorex,sitename)
    inputs['landsat_collection'] = 'C02'
    inputs['dates'] =  ['1984-01-01', '2022-01-01']
    inputs['sat_list'] = ['L5','L7','L8','L9','S2']
    inputs['sitename'] = sitename
    # load settings file
    fp_settings = 'settings_shoreline_mapping.txt'
    with open(fp_settings,'r') as f: settings = json.load(f)
    settings['inputs'] = inputs
    # take epsg from sites_info 
    settings['output_epsg'] = epsgs[sitename]
    # load reference shoreline
    fn_refsl = os.path.join(data_folder, '%s_reference_shoreline.geojson'%sitename)
    gdf_refsl = gpd.read_file(fn_refsl)
    print('Loaded reference shoreline in epsg:%d'%gdf_refsl.crs.to_epsg(), end='...')
    gdf_refsl.to_crs(epsg=settings['output_epsg'], inplace=True)
    print('converted to epsg:%d'%gdf_refsl.crs.to_epsg())
    refsl = np.array(gdf_refsl.loc[0,'geometry'].coords)
    settings['reference_shoreline'] = refsl
    # load transects
    fn_transects = os.path.join(data_folder, '%s_transects.geojson'%sitename)
    gdf_transects = gpd.read_file(fn_transects)
    print('Loaded transects in epsg:%d'%gdf_transects.crs.to_epsg(), end='...')
    gdf_transects.to_crs(epsg=settings['output_epsg'], inplace=True)
    print('converted to epsg:%d'%gdf_transects.crs.to_epsg())
    # put transects into a dictionary with their name
    transects = dict([])
    for i in gdf_transects.index:
        transects[gdf_transects.loc[i,'name']] = np.array(gdf_transects.loc[i,'geometry'].coords)
    fig,ax = plt.subplots(1,1,figsize=[15,8], tight_layout=True)
    ax.axis('equal')
    ax.set(xlabel='Eastings',ylabel='Northings',title='%s - satellite-derived shorelines and transect locations'%sitename)
    ax.grid(linestyle=':', color='0.5')
    for i in range(len(output['shorelines'])):
        sl = output['shorelines'][i]
        date = output['dates'][i]
        ax.plot(sl[:,0], sl[:,1], '.', label=date.strftime('%d-%m-%Y'))
    for i,key in enumerate(list(transects.keys())):
        ax.plot(transects[key][0,0],transects[key][0,1], 'bo', ms=5)
        ax.plot(transects[key][:,0],transects[key][:,1],'k-',lw=1)
        if len(transects) < 50: ax.text(transects[key][0,0]-100, transects[key][0,1]+100, key,va='center', ha='right')
    ax.plot(refsl[:,0],refsl[:,1],'k--')
    fig.savefig(os.path.join(inputs['filepath'], 'mapped_shorelines.jpg'),dpi=200)
    #########################################################################################################
    # Compute intersections
    #########################################################################################################
    # load settings file
    fp_settings = 'settings_transect_intersections.txt'
    with open(fp_settings,'r') as f: settings_transects = json.load(f)
    cross_distance = SDS_transects.compute_intersection_QC(output, transects, settings_transects)
    #########################################################################################################
    # Tidal correction
    #########################################################################################################
    # load tide time-series
    fn_tides = os.path.join(data_folder,'%s_tides.csv'%sitename)
    tide_data = pd.read_csv(fn_tides, parse_dates=['dates'])
    dates_ts = [pytz.utc.localize(_.to_pydatetime()) for _ in tide_data['dates']]
    tides_ts = np.array(tide_data['tides'])
    # get tide levels corresponding to the time of image acquisition
    dates_sat = output['dates']
    tides_sat = SDS_tools.get_closest_datapoint(dates_sat, dates_ts, tides_ts)
    # plot the subsampled tide data
    fig, ax = plt.subplots(1,1,figsize=(15,4), tight_layout=True)
    ax.grid(which='major', linestyle=':', color='0.5')
    ax.plot(tide_data['dates'], tide_data['tides'], '-', color='0.6', label='all time-series')
    ax.plot(dates_sat, tides_sat, '-o', color='k', ms=6, mfc='w',lw=1, label='image acquisition')
    ax.set(ylabel='tide level [m]',xlim=[dates_sat[0],dates_sat[-1]], title='%s - water levels at the time of image acquisition'%sitename)
    ax.legend()
    fig.savefig(os.path.join(inputs['filepath'], 'tide_timeseries.jpg'),dpi=200)
    # tidal correction along each transect
    ref_elev = {'MSL':0,'MHWS':sites_info[sitename]['contour_level']}
    beach_slope = sites_info[sitename]['beach_slope']     # beach slope, uniform for all transects
    fp_raw_timeseries = os.path.join(fp_shorex,sitename, 'raw_timeseries')
    if not os.path.exists(fp_raw_timeseries): os.makedirs(fp_raw_timeseries)
    # repeat for MSL and MHWS
    for c in ref_elev.keys():
        reference_elevation = ref_elev[c] # elevation at which you would like the shoreline time-series to be
        cross_distance_tidally_corrected, tidal_corrections = {},{}
        for key in cross_distance.keys():
            correction = (tides_sat-reference_elevation)/beach_slope
            tidal_corrections[key] = correction
            cross_distance_tidally_corrected[key] = cross_distance[key] + correction
        if sitename == 'TRUCVERT':     # remove low tide images for TRUCVERT only (based on Castelle et al. 2021)
            for key in cross_distance_tidally_corrected.keys():
                for i in range(len(cross_distance_tidally_corrected[key])):
                    if tides_sat[i] < 0.2: cross_distance_tidally_corrected[key][i] = np.nan
        # remove outliers
        print('\nRemoving outliers...')
        settings_transects['otsu_threshold'] = [np.nan, np.nan]
        # settings_transects['plot_fig'] = True
        cross_distance_tidally_corrected = SDS_transects.reject_outliers(cross_distance_tidally_corrected,output,settings_transects)
        # save in .csv files
        output_folder = 'tidally_corrected_timeseries_%s'%c
        fp_tc_timeseries = os.path.join(fp_shorex,sitename,output_folder)
        if not os.path.exists(fp_tc_timeseries): os.makedirs(fp_tc_timeseries)
        for key in cross_distance_tidally_corrected.keys():
            out_dict = dict([])
            out_dict['dates'] = output['dates']
            out_dict[key] = cross_distance_tidally_corrected[key]
            out_dict['satname'] = output['satname']
            df = pd.DataFrame(out_dict)
            df.index=df['dates']
            df.pop('dates')
            # save tidally_corrected timeseries
            fn = os.path.join(fp_tc_timeseries,'%s_timeseries_tidally_corrected.csv'%key)
            df.to_csv(fn, sep=',')
            # save raw timeseries
            if c == 'MSL':
                out_dict[key] = cross_distance_tidally_corrected[key] - tidal_corrections[key]
                df = pd.DataFrame(out_dict)
                df.index=df['dates']
                df.pop('dates')
                fn = os.path.join(fp_raw_timeseries,'%s_timeseries_raw.csv'%key)
                df.to_csv(fn, sep=',')
        # plot time-series
        fp_plots = os.path.join(fp_shorex,sitename,'plots_%s'%c)
        if not os.path.exists(fp_plots): os.makedirs(fp_plots)
        month_colors = plt.cm.get_cmap('tab20')
        for key in cross_distance_tidally_corrected.keys():
            chainage = cross_distance_tidally_corrected[key]
            # remove nans
            idx_nan = np.isnan(chainage)
            dates_nonan = [dates_sat[_] for _ in np.where(~idx_nan)[0]]
            chainage = chainage[~idx_nan] 
            # compute shoreline monthly averages
            dict_month, dates_month, chainage_month, list_month = SDS_transects.monthly_average(dates_nonan, chainage)
            # plot monthly averages
            fig,ax=plt.subplots(1,1,figsize=[14,4],tight_layout=True)
            ax.grid(b=True,which='major', linestyle=':', color='0.5')
            ax.set_title('Time-series at %s'%key, x=0, ha='left')
            ax.set(ylabel='distance [m]')
            ax.plot(dates_nonan, chainage,'+', lw=1, color='k', mfc='w', ms=4, alpha=0.5,label='raw datapoints')
            ax.plot(dates_month, chainage_month, '-', lw=2, color='k', mfc='w', ms=4, label='monthly-averaged')
            # for k,month in enumerate(dict_month.keys()):
            #     ax.plot(dict_month[month]['dates'], dict_month[month]['chainages'],
            #              'o', mec='k', color=month_colors(k), label=month,ms=5)
            ax.legend(loc='lower left',ncol=7,markerscale=1.5,frameon=True,edgecolor='k',columnspacing=1)
            fig.savefig(os.path.join(fp_plots,'%s_timeseries.jpg'%key),dpi=200)
            plt.close(fig)
    


    
