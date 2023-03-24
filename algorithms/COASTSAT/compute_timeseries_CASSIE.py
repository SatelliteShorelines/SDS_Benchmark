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

# load settings file for outliuer detection
fp_settings = 'settings_transect_intersections.txt'
with open(fp_settings,'r') as f: settings_transects = json.load(f)
settings_transects['max_cross_change'] = 50
settings_transects['otsu_threshold'] = [np.nan, np.nan]
settings_transects['plot_fig'] = False

#%% Compute intersections and tidally correct to MSL and MHWS

selected_transects = {
    'NARRABEEN': ['PF1','PF2','PF4','PF6','PF8'],
    'DUCK':      ['-91','1','1006','1097'],
    'TRUCVERT':   ['-400','-300','-200','-100'],
    'TORREYPINES':['PF525','PF535','PF585','PF595'],    
    }

# For Landsat
fp_cassie = os.path.join(os.pardir,os.pardir,'submissions','team_CASSIE')
for sitename in names_datasets:
    if sitename in ['CALAMILLOR']: continue
    print('\n%s'%sitename)
    # locate submitted time-series
    fp_timeseries = os.path.join(fp_cassie,sitename,'raw_timeseries')
    date_str = 'dates'
    chain_str = 'Distance'
    # load dataset inputs
    data_folder = os.path.join(fp_datasets,sitename)
    # load time-series
    fn_transects = os.listdir(fp_timeseries)
    cross_distance = {}
    for i,fn in enumerate(fn_transects):
        fp = os.path.join(fp_timeseries,fn)
        # get transect name from filename
        key = fn.split('_')[0]
        key = key.split('.csv')[0]
        if not key in selected_transects[sitename]: continue
        # read csv file and extract dates and chainages
        df = pd.read_csv(fp,sep=', ',names=['dates','Distance','satname'],
                         skiprows=1)
        for k in range(len(df)):
            df.at[k,'dates'] = df.at[k,'dates'][1:]
            df.at[k,'satname'] = df.at[k,'satname'][:-1]
        chainage = np.array(df['Distance'])
        dates_sat = [pytz.utc.localize(datetime.strptime(_[:-6],'%Y-%m-%d %H:%M:%S')) for _ in df['dates']] 
        if sitename in ['TORREYPINES','TRUCVERT']:
            cross_distance[key] = {'chainage':chainage,
                                   'dates': dates_sat}
        else:
            idx_nonan = np.where(~np.isnan(chainage))[0]
            chainage1 = [chainage[k] for k in idx_nonan]
            dates1 = [dates_sat[k] for k in idx_nonan]
            chainage2, dates2 = SDS_transects.identify_outliers(list(chainage1), dates1, settings_transects['max_cross_change'])
            cross_distance[key] = {'chainage':np.array(chainage2),
                                    'dates': dates2}
            # figure for QA
            if settings_transects['plot_fig']:
                fig,ax=plt.subplots(1,1,figsize=[12,6], sharex=True)
                fig.set_tight_layout(True)
                ax.grid(linestyle=':', color='0.5')
                ax.set(ylabel='distance [m]',
                          title= 'Transect %s original time-series - %d points' % (key, len(chainage)))
                mean_cross_dist = np.nanmedian(chainage1)
                # plot the data points
                ax.plot(dates1, chainage1-mean_cross_dist, 'C0-')
                ax.plot(dates1, chainage1-mean_cross_dist, 'C3o', ms=4, mec='k', mew=0.7,label='spike')
                # plot the indices removed because of the threshold
                ax.plot(dates2, chainage2-mean_cross_dist, 'C2o', ms=4, mec='k', mew=0.7,label='kept')
                ax.legend(ncol=2,loc='upper right')
                # plot the final time-series
                print('%s  - outliers removed: %d'%(key, len(dates1) - len(dates2)))
    #########################################################################################################
    # Tidal correction
    #########################################################################################################
    ref_elev = {'MSL':0,'MHWS':sites_info[sitename]['contour_level']}
    beach_slope = sites_info[sitename]['beach_slope']     # beach slope, uniform for all transects
    # load tide time-series
    fn_tides = os.path.join(data_folder,'%s_tides.csv'%sitename)
    tide_data = pd.read_csv(fn_tides, parse_dates=['dates'])
    dates_ts = [pytz.utc.localize(_.to_pydatetime()) for _ in tide_data['dates']]
    tides_ts = np.array(tide_data['tides'])
    # get tide levels corresponding to the time of image acquisition
    for key in cross_distance.keys():
        print(key)
        # if os.path.exists(os.path.join(fp_cassie,sitename,
        #                                'tidally_corrected_timeseries_MHWS',
        #                                '%s_timeseries_tidally_corrected.csv'%key)):
        #     continue
        dates_sat = cross_distance[key]['dates']
        tides_sat = SDS_tools.get_closest_datapoint(dates_sat, dates_ts, tides_ts)
        # repeat for MSL and MHWS
        for c in ref_elev.keys():
            reference_elevation = ref_elev[c] # elevation at which you would like the shoreline time-series to be
            correction = (tides_sat-reference_elevation)/beach_slope
            cross_distance[key]['chainage_%s'%c] = cross_distance[key]['chainage'] + correction
            if sitename == 'TRUCVERT':     # remove low tide images for TRUCVERT only (based on Castelle et al. 2021)
                for i in range(len(tides_sat)):
                    if tides_sat[i] < 0.2: cross_distance[key]['chainage_%s'%c][i] = np.nan

    # save in .csv files
    for c in ref_elev.keys():
        output_folder = 'tidally_corrected_timeseries_%s'%c
        fp_tc_timeseries = os.path.join(fp_cassie,sitename,output_folder)
        if not os.path.exists(fp_tc_timeseries): os.makedirs(fp_tc_timeseries)
        for key in cross_distance.keys():
            # if os.path.exists(os.path.join(fp_tc_timeseries,'%s_timeseries_tidally_corrected.csv'%key)):
            #     continue
            out_dict = dict([])
            out_dict['dates'] = cross_distance[key]['dates']
            out_dict[key] = cross_distance[key]['chainage_%s'%c]
            out_dict['satname'] = ['Landsat' for _ in range(len(cross_distance[key]['dates']))]
            df = pd.DataFrame(out_dict)
            df.index=df['dates']
            df.pop('dates')
            # save tidally_corrected timeseries
            fn = os.path.join(fp_tc_timeseries,'%s_timeseries_tidally_corrected.csv'%key)
            df.to_csv(fn, sep=',')
                
#%% For Sentinel-2
fp_cassie = os.path.join(os.pardir,os.pardir,'submissions','team_CASSIE')
for sitename in names_datasets:
    if sitename in ['CALAMILLOR']: continue
    print('\n%s'%sitename)
    # locate submitted time-series
    fp_timeseries = os.path.join(fp_cassie,sitename,'raw_timeseries_S2')
    date_str = 'dates'
    chain_str = 'Distance'
    # load dataset inputs
    data_folder = os.path.join(fp_datasets,sitename)
    # load time-series
    fn_transects = os.listdir(fp_timeseries)
    cross_distance = {}
    for i,fn in enumerate(fn_transects):
        fp = os.path.join(fp_timeseries,fn)
        # get transect name from filename
        key = fn.split('_')[0]
        key = key.split('.csv')[0]
        if not key in selected_transects[sitename]: continue
        # read csv file and extract dates and chainages
        df = pd.read_csv(fp,sep=', ',names=['dates','Distance','satname'],
                         skiprows=1)
        for k in range(len(df)):
            df.at[k,'dates'] = df.at[k,'dates'][1:]
            df.at[k,'satname'] = df.at[k,'satname'][:-1]
        chainage = np.array(df['Distance'])
        dates_sat = [pytz.utc.localize(datetime.strptime(_[:-6],'%Y-%m-%d %H:%M:%S')) for _ in df['dates']] 
        if sitename in ['TORREYPINES','TRUCVERT']:
            cross_distance[key] = {'chainage':chainage,
                                   'dates': dates_sat}
        else:
            idx_nonan = np.where(~np.isnan(chainage))[0]
            chainage1 = [chainage[k] for k in idx_nonan]
            dates1 = [dates_sat[k] for k in idx_nonan]
            chainage2, dates2 = SDS_transects.identify_outliers(list(chainage1), dates1, settings_transects['max_cross_change'])
            cross_distance[key] = {'chainage':np.array(chainage2),
                                    'dates': dates2}
            # figure for QA
            if settings_transects['plot_fig']:
                fig,ax=plt.subplots(1,1,figsize=[12,6], sharex=True)
                fig.set_tight_layout(True)
                ax.grid(linestyle=':', color='0.5')
                ax.set(ylabel='distance [m]',
                          title= 'Transect %s original time-series - %d points' % (key, len(chainage)))
                mean_cross_dist = np.nanmedian(chainage1)
                # plot the data points
                ax.plot(dates1, chainage1-mean_cross_dist, 'C0-')
                ax.plot(dates1, chainage1-mean_cross_dist, 'C3o', ms=4, mec='k', mew=0.7,label='spike')
                # plot the indices removed because of the threshold
                ax.plot(dates2, chainage2-mean_cross_dist, 'C2o', ms=4, mec='k', mew=0.7,label='kept')
                ax.legend(ncol=2,loc='upper right')
                # plot the final time-series
                print('%s  - outliers removed: %d'%(key, len(dates1) - len(dates2)))
    #########################################################################################################
    # Tidal correction
    #########################################################################################################
    ref_elev = {'MSL':0,'MHWS':sites_info[sitename]['contour_level']}
    beach_slope = sites_info[sitename]['beach_slope']     # beach slope, uniform for all transects
    # load tide time-series
    fn_tides = os.path.join(data_folder,'%s_tides.csv'%sitename)
    tide_data = pd.read_csv(fn_tides, parse_dates=['dates'])
    dates_ts = [pytz.utc.localize(_.to_pydatetime()) for _ in tide_data['dates']]
    tides_ts = np.array(tide_data['tides'])
    # get tide levels corresponding to the time of image acquisition
    for key in cross_distance.keys():
        print(key)
        # if os.path.exists(os.path.join(fp_cassie,sitename,
        #                                'tidally_corrected_timeseries_MHWS_S2',
        #                                '%s_timeseries_tidally_corrected.csv'%key)):
        #     continue
        dates_sat = cross_distance[key]['dates']
        tides_sat = SDS_tools.get_closest_datapoint(dates_sat, dates_ts, tides_ts)
        # repeat for MSL and MHWS
        for c in ref_elev.keys():
            reference_elevation = ref_elev[c] # elevation at which you would like the shoreline time-series to be
            correction = (tides_sat-reference_elevation)/beach_slope
            cross_distance[key]['chainage_%s'%c] = cross_distance[key]['chainage'] + correction
            if sitename == 'TRUCVERT':     # remove low tide images for TRUCVERT only (based on Castelle et al. 2021)
                for i in range(len(tides_sat)):
                    if tides_sat[i] < 0.2: cross_distance[key]['chainage_%s'%c][i] = np.nan
    # save in .csv files
    for c in ref_elev.keys():
        output_folder = 'tidally_corrected_timeseries_%s_S2'%c
        fp_tc_timeseries = os.path.join(fp_cassie,sitename,output_folder)
        if not os.path.exists(fp_tc_timeseries): os.makedirs(fp_tc_timeseries)
        for key in cross_distance.keys():
            # if os.path.exists(os.path.join(fp_tc_timeseries,'%s_timeseries_tidally_corrected.csv'%key)):
            #     continue
            out_dict = dict([])
            out_dict['dates'] = cross_distance[key]['dates']
            out_dict[key] = cross_distance[key]['chainage_%s'%c]
            out_dict['satname'] = ['Landsat' for _ in range(len(cross_distance[key]['dates']))]
            df = pd.DataFrame(out_dict)
            df.index=df['dates']
            df.pop('dates')
            # save tidally_corrected timeseries
            fn = os.path.join(fp_tc_timeseries,'%s_timeseries_tidally_corrected.csv'%key)
            df.to_csv(fn, sep=',')