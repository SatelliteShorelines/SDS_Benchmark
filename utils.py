"""
This module contains utilities for SDS_Benchmark
    
"""

# load modules
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from datetime import datetime, timedelta
import pytz
import pdb

# other modules
import skimage.transform as transform
from scipy import interpolate
from scipy import stats

###################################################################################################
# UTILITIES
###################################################################################################

def get_closest_datapoint(dates, dates_ts, values_ts):
    """
    Extremely efficient script to get closest data point to a set of dates from a very
    long time-series (e.g., 15-minutes tide data, or hourly wave data)
    
    Make sure that dates and dates_ts are in the same timezone (also aware or naive)
    
    KV WRL 2020

    Arguments:
    -----------
    dates: list of datetimes
        dates at which the closest point from the time-series should be extracted
    dates_ts: list of datetimes
        dates of the long time-series
    values_ts: np.array
        array with the values of the long time-series (tides, waves, etc...)
        
    Returns:    
    -----------
    values: np.array
        values corresponding to the input dates
        
    """
    
    # check if the time-series cover the dates
    if dates[0] < dates_ts[0] or dates[-1] > dates_ts[-1]: 
        raise Exception('Time-series do not cover the range of your input dates')
    
    # get closest point to each date (no interpolation)
    temp = []
    def find(item, lst):
        start = 0
        start = lst.index(item, start)
        return start
    for i,date in enumerate(dates):
        print('\rExtracting closest points: %d%%' % int((i+1)*100/len(dates)), end='')
        temp.append(values_ts[find(min(item for item in dates_ts if item > date), dates_ts)])
    values = np.array(temp)
    
    return values

###################################################################################################
# SEASONAL/MONTHLY AVERAGING
###################################################################################################

def seasonal_average(dates, chainages): 
    # define the 4 seasons
    months = ['-%02d'%_ for _ in np.arange(1,13)]
    seasons = np.array([1,4,7,10])
    season_labels = ['DJF', 'MAM', 'JJA', 'SON']
    # put time-series into a pd.dataframe (easier to process)
    df = pd.DataFrame({'dates': dates, 'chainage':chainages})
    df.set_index('dates', inplace=True) 
    # initialise variables for seasonal averages
    dict_seasonal = dict([])
    for k,j in enumerate(seasons):
        dict_seasonal[season_labels[k]] = {'dates':[], 'chainages':[]}
    dates_seasonal = []
    chainage_seasonal = []
    season_ts = []
    for year in np.unique(df.index.year):
        # 4 seasons: DJF, MMA, JJA, SON
        for k,j in enumerate(seasons):
            # middle date
            date_seas = pytz.utc.localize(datetime(year,j,1))
            # if j == 1: date_seas = pytz.utc.localize(datetime(year-1,12,31))
            # for the first season, take the December data from the year before
            if j == 1:
                chain_seas = np.array(df[str(year-1) + months[(j-1)-1]:str(year) + months[(j-1)+1]]['chainage'])
            else:
                chain_seas = np.array(df[str(year) + months[(j-1)-1]:str(year) + months[(j-1)+1]]['chainage'])
            if len(chain_seas) == 0:
                continue
            else:
                dict_seasonal[season_labels[k]]['dates'].append(date_seas)
                dict_seasonal[season_labels[k]]['chainages'].append(np.mean(chain_seas))
                dates_seasonal.append(date_seas)
                chainage_seasonal.append(np.mean(chain_seas))
                season_ts.append(j)
    # convert chainages to np.array (easier to manipulate than a list)
    for seas in dict_seasonal.keys():
         dict_seasonal[seas]['chainages'] = np.array(dict_seasonal[seas]['chainages'])
                
    return dict_seasonal, dates_seasonal, np.array(chainage_seasonal), np.array(season_ts)

def monthly_average(dates, chainages):
    # define the 12 months
    months = ['-%02d'%_ for _ in np.arange(1,13)]
    seasons = np.arange(1,13)
    season_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # put time-series into a pd.dataframe (easier to process)
    df = pd.DataFrame({'dates': dates, 'chainage':chainages})
    df.set_index('dates', inplace=True) 
    # initialise variables for seasonal averages
    dict_seasonal = dict([])
    for k,j in enumerate(seasons):
        dict_seasonal[season_labels[k]] = {'dates':[], 'chainages':[]}
    dates_seasonal = []
    chainage_seasonal = []
    season_ts = []
    for year in np.unique(df.index.year):
        # 4 seasons: DJF, MMA, JJA, SON
        for k,j in enumerate(seasons):
            # middle date
            date_seas = pytz.utc.localize(datetime(year,j,15))
            if date_seas > dates[-1] - timedelta(days=30):
                break
            try:
                chain_seas = np.array(df[str(year) + months[k]]['chainage'])
            except:
                continue
            if len(chain_seas) == 0:
                continue
            else:
                dict_seasonal[season_labels[k]]['dates'].append(date_seas)
                dict_seasonal[season_labels[k]]['chainages'].append(np.mean(chain_seas))
                dates_seasonal.append(date_seas)
                chainage_seasonal.append(np.mean(chain_seas))
                season_ts.append(j)
    # convert chainages to np.array (easier to manipulate than a list)
    for seas in dict_seasonal.keys():
         dict_seasonal[seas]['chainages'] = np.array(dict_seasonal[seas]['chainages'])
                
    return dict_seasonal, dates_seasonal, np.array(chainage_seasonal), np.array(season_ts)

###################################################################################################
# COMPARISON WITH GROUNDTRUTH
###################################################################################################

def compare_timeseries(ts,gt,key,settings):
    "Compares time-series using by interpolating the groundtruth around the satellite data, see compare_timeseries2 for the other way around"
    if key not in gt.keys():
        raise Exception('transect name %s does not exist in grountruth file'%key)
    if isinstance(ts, pd.DataFrame):
        # remove nans
        chainage = np.array(ts[key])
        idx_nan = np.isnan(chainage)
        dates_nonans = [ts['dates'][k].to_pydatetime() for k in np.where(~idx_nan)[0]]
        satnames_nonans = [ts['satname'][k] for k in np.where(~idx_nan)[0]]
        chain_nonans = chainage[~idx_nan]
    else:
        chain_nonans = ts['chainage']
        dates_nonans = ts['dates']
        satnames_nonans = ['Landsat' for _ in range(len(ts['dates']))]
    # define satellite and survey time-series
    chain_sat_dm = chain_nonans
    if 'chainage' in gt[key].keys():
        chain_str = 'chainage'
    elif 'chainages' in gt[key].keys():
        chain_str = 'chainages'
    chain_sur_dm = gt[key][chain_str]

    # plot the time-series
    fig= plt.figure(figsize=[15,8], tight_layout=True)
    gs = gridspec.GridSpec(2,3)
    ax0 = fig.add_subplot(gs[0,:])
    ax0.grid(b=True,which='major',linestyle=':',color='0.5')
    ax0.plot(gt[key]['dates'], chain_sur_dm,'C1-',label='in situ')
    ax0.plot(dates_nonans, chain_sat_dm,'C0-',label='satellite')
    date_start = np.max([gt[key]['dates'][0],dates_nonans[0]])
    date_last = np.min([gt[key]['dates'][-1],dates_nonans[-1]])
    ax0.set(title= 'Transect ' + key, xlim=[date_start-timedelta(days=30),
                                            date_last+timedelta(days=30)]) 
    ax0.legend(ncol=2)
    
    # interpolate surveyed data around satellite data based on the parameters (min_days and max_days)
    chain_int = np.nan*np.ones(len(dates_nonans))
    for k,date in enumerate(dates_nonans):
        # compute the days distance for each satellite date
        days_diff = np.array([ (_ - date).days for _ in gt[key]['dates']])
        # if nothing within max_days put a nan
        if np.min(np.abs(days_diff)) > settings['max_days']:
            chain_int[k] = np.nan
        else:
            # if a point within min_days, take that point (no interpolation)
            if np.min(np.abs(days_diff)) < settings['min_days']:
                idx_closest = np.where(np.abs(days_diff) == np.min(np.abs(days_diff)))
                chain_int[k] = float(gt[key][chain_str][idx_closest[0][0]])
            else: # otherwise, between min_days and max_days, interpolate between the 2 closest points
                if sum(days_diff > 0) == 0:
                    break
                idx_after = np.where(days_diff > 0)[0][0]
                idx_before = idx_after - 1
                x = [gt[key]['dates'][idx_before].toordinal() , gt[key]['dates'][idx_after].toordinal()]
                y = [gt[key][chain_str][idx_before], gt[key][chain_str][idx_after]]
                f = interpolate.interp1d(x, y,bounds_error=True)
                try:
                    chain_int[k] = float(f(date.toordinal()))
                except:
                    chain_int[k] = np.nan
                        
    # remove nans again
    idx_nan = np.isnan(chain_int)
    chain_sat = chain_nonans[~idx_nan]
    chain_sur = chain_int[~idx_nan]
    dates_sat = [dates_nonans[k] for k in np.where(~idx_nan)[0]]
    satnames = [satnames_nonans[k] for k in np.where(~idx_nan)[0]]
    if len(chain_sat) < 8 or len(chain_sur) < 8: 
        print('not enough data points for comparison at transect %s'%key)
        plt.close(fig)
        return  chain_sat, chain_sur, satnames, []
                        
    # error statistics
    slope, intercept, rvalue, pvalue, std_err = stats.linregress(chain_sur, chain_sat)
    R2 = rvalue**2
    chain_error = chain_sat - chain_sur
    rmse = np.sqrt(np.mean((chain_error)**2))
    mean = np.mean(chain_error)
    std = np.std(chain_error)
    q90 = np.percentile(np.abs(chain_error), 90)
    gof = 1- np.sum((chain_sat - chain_sur)**2)/(np.sum((np.abs(chain_sat-np.mean(chain_sur))+np.abs(chain_sur-np.mean(chain_sur)))**2))
    
    # 1:1 plot
    ax1 = fig.add_subplot(gs[1,0])
    ax1.axis('equal')
    ax1.grid(which='major',linestyle=':',color='0.5')
    for k,sat in enumerate(list(np.unique(satnames))):
        idx = np.where([_ == sat for _ in satnames])[0]
        ax1.plot(chain_sur[idx], chain_sat[idx], 'o', ms=4, mfc='C'+str(k),mec='C'+str(k), alpha=0.7, label=sat)
    ax1.legend(loc=4)
    ax1.plot([ax1.get_xlim()[0], ax1.get_ylim()[1]],[ax1.get_xlim()[0], ax1.get_ylim()[1]],'k--',lw=2)
    ax1.set(xlabel='survey [m]', ylabel='satellite [m]')   
    ax1.text(0.01,0.98,'R2 = %.2f\nGoF = %.2f'%(R2,gof),bbox=dict(boxstyle='square', facecolor='w', alpha=1),transform=ax1.transAxes,
            ha='left',va='top')

    # boxplots
    ax2 = fig.add_subplot(gs[1,1])
    data = []
    median_data = []
    n_data = []
    ax2.yaxis.grid()
    for k,sat in enumerate(list(np.unique(satnames))):
        idx = np.where([_ == sat for _ in satnames])[0]
        data.append(chain_error[idx])
        median_data.append(np.median(chain_error[idx]))
        n_data.append(len(chain_error[idx]))
    bp = ax2.boxplot(data,0,'k.', labels=list(np.unique(satnames)), patch_artist=True)
    for median in bp['medians']:
        median.set(color='k', linewidth=1.5)
    for j,boxes in enumerate(bp['boxes']):
        boxes.set(facecolor='C'+str(j))
        ax2.text(j+1,median_data[j]+1, '%.1f' % median_data[j], horizontalalignment='center', fontsize=12)
        ax2.text(j+1+0.35,median_data[j]+1, ('n=%.d' % int(n_data[j])), ha='center', va='center', fontsize=12,
                 rotation='vertical')
    ax2.set(ylabel='error [m]', ylim=settings['lims'])
    
    # histogram
    ax3 = fig.add_subplot(gs[1,2])
    ax3.grid(which='major',linestyle=':',color='0.5')
    ax3.axvline(x=0, ls='--', lw=1.5, color='k')
    binwidth = settings['binwidth']
    bins = np.arange(min(chain_error), max(chain_error) + binwidth, binwidth)
    density = plt.hist(chain_error, bins=bins, density=True, color='0.6', edgecolor='k', alpha=0.5)
    mu, std = stats.norm.fit(chain_error)
    pval = stats.normaltest(chain_error)[1]
    xlims = ax3.get_xlim()
    x = np.linspace(xlims[0], xlims[1], 100)
    p = stats.norm.pdf(x, mu, std)
    ax3.plot(x, p, 'r-', linewidth=1)
    ax3.set(xlabel='error [m]', ylabel='pdf', xlim=settings['lims'])
    str_stats = ' rmse = %.1f\n mean = %.1f\n std = %.1f\n q90 = %.1f' % (rmse, mean, std, q90)
    ax3.text(0, 0.98, str_stats,va='top', transform=ax3.transAxes)    
    
    return chain_sat, chain_sur, satnames, fig


def compare_timeseries2(ts,gt,key,settings):
    "Compares time-series using by interpolating the satellite data around the groundtruth, see compare_timeseries for the other way around"
    if key not in gt.keys():
        raise Exception('transect name %s does not exist in grountruth file'%key)
    if isinstance(ts, pd.DataFrame):
        # remove nans
        chainage = np.array(ts[key])
        idx_nan = np.isnan(chainage)
        dates_nonans = [ts['dates'][k].to_pydatetime() for k in np.where(~idx_nan)[0]]
        satnames_nonans = [ts['satname'][k] for k in np.where(~idx_nan)[0]]
        chain_nonans = chainage[~idx_nan]
    else:
        chain_nonans = ts['chainage']
        dates_nonans = ts['dates']
        satnames_nonans = ['Landsat' for _ in range(len(ts['dates']))]
    # define satellite and survey time-series
    chain_sat_dm = chain_nonans
    if 'chainage' in gt[key].keys():
        chain_str = 'chainage'
    elif 'chainages' in gt[key].keys():
        chain_str = 'chainages'
    chain_sur_dm = np.array([float(_) for _ in gt[key][chain_str]])
    # remove nans
    idx_nan = np.isnan(chain_sur_dm)
    dates_sur = [gt[key]['dates'][k] for k in np.where(~idx_nan)[0]]
    chain_sur_dm = chain_sur_dm[~idx_nan]

    # plot the time-series
    fig= plt.figure(figsize=[15,8], tight_layout=True)
    gs = gridspec.GridSpec(2,3)
    ax0 = fig.add_subplot(gs[0,:])
    ax0.grid(b=True,which='major',linestyle=':',color='0.5')
    ax0.plot(dates_sur, chain_sur_dm,'C1-',label='in situ')
    ax0.plot(dates_nonans, chain_sat_dm,'C0-',label='satellite')
    date_start = np.max([dates_sur[0],dates_nonans[0]])
    date_last = np.min([dates_sur[-1],dates_nonans[-1]])
    ax0.set(title='Transect ' + key, xlim=[date_start-timedelta(days=30),
                                            date_last+timedelta(days=30)]) 
    ax0.legend(ncol=2)

    # interpolate surveyed data around satellite data based on the parameters (min_days and max_days)
    chain_int, dates_int, sat_int, idx_int = [],[],[],[] 
    for k,date in enumerate(dates_sur):
        # compute the days distance for each satellite date
        days_diff = np.array([ (_ - date).days for _ in dates_nonans])
        # if nothing within max_days put a nan
        if np.min(np.abs(days_diff)) <= settings['max_days']:
            # if a point within min_days, take that point (no interpolation)
            if np.min(np.abs(days_diff)) < settings['min_days']:
                idx_closest = np.where(np.abs(days_diff) == np.min(np.abs(days_diff)))[0][0]
                chain_int.append(chain_sat_dm[idx_closest])
                dates_int.append(date)
                sat_int.append(satnames_nonans[idx_closest])
                idx_int.append(k)
            else: # otherwise, between min_days and max_days, interpolate between the 2 closest points
                if sum(days_diff < 0) == 0 or sum(days_diff > 0) == 0:
                    continue
                idx_after = np.where(days_diff > 0)[0][0]
                idx_before = idx_after - 1
                x = [dates_nonans[idx_before].toordinal() , dates_nonans[idx_after].toordinal()]
                y = [chain_sat_dm[idx_before], chain_sat_dm[idx_after]]
                f = interpolate.interp1d(x, y,bounds_error=True)
                try:
                    chain_int.append(float(f(date.toordinal())))
                    dates_int.append(date)
                    sat_int.append(satnames_nonans[idx_before])
                    idx_int.append(k)
                except:
                    continue
    ax0.plot(dates_sur, chain_sur_dm,'C1o',mfc='none',ms=4)
    ax0.plot(dates_nonans,chain_nonans,'C0o',mfc='none',ms=4)
    ax0.plot(dates_int,chain_int,'ko',mfc='none',ms=4)

    
    ax0.set_title('Transect %s - n_sur = %d - n_sat = %d - n_int = %d'%(key,
                                                                        len(dates_sur),
                                                                        len(dates_nonans),
                                                                        len(dates_int)))

    if len(chain_int) == 0:
        print('not enough data points for comparison at transect %s'%key)
        plt.close(fig)
        return  [], [], [], fig       
    
    # remove nans again
    chain_int = np.array(chain_int)
    idx_nan = np.isnan(chain_int)
    chain_sat = chain_int[~idx_nan]
    chain_sur = chain_sur_dm[np.array(idx_int)][~idx_nan]
    dates_sat = [dates_int[k] for k in np.where(~idx_nan)[0]]
    satnames = [sat_int[k] for k in np.where(~idx_nan)[0]]
    
    # make sure there's enough data point to compute the metrics
    if len(chain_sat) < 8 or len(chain_sur) < 8: 
        print('not enough data points for comparison at transect %s'%key)
        plt.close(fig)
        return  chain_sat, chain_sur, satnames, fig
                        
    # error statistics
    slope, intercept, rvalue, pvalue, std_err = stats.linregress(chain_sur, chain_sat)
    R2 = rvalue**2
    chain_error = chain_sat - chain_sur
    rmse = np.sqrt(np.mean((chain_error)**2))
    mean = np.mean(chain_error)
    std = np.std(chain_error)
    q90 = np.percentile(np.abs(chain_error), 90)
    gof = 1- np.sum((chain_sat - chain_sur)**2)/(np.sum((np.abs(chain_sat-np.mean(chain_sur))+np.abs(chain_sur-np.mean(chain_sur)))**2))
    
    # 1:1 plot
    ax1 = fig.add_subplot(gs[1,0])
    ax1.axis('equal')
    ax1.grid(which='major',linestyle=':',color='0.5')
    for k,sat in enumerate(list(np.unique(satnames))):
        idx = np.where([_ == sat for _ in satnames])[0]
        ax1.plot(chain_sur[idx], chain_sat[idx], 'o', ms=4, mfc='C'+str(k),mec='C'+str(k), alpha=0.7, label=sat)
    ax1.legend(loc=4)
    ax1.plot([ax1.get_xlim()[0], ax1.get_ylim()[1]],[ax1.get_xlim()[0], ax1.get_ylim()[1]],'k--',lw=2)
    ax1.set(xlabel='survey [m]', ylabel='satellite [m]')   
    ax1.text(0.01,0.98,'R2 = %.2f\nGoF = %.2f'%(R2,gof),bbox=dict(boxstyle='square', facecolor='w', alpha=1),transform=ax1.transAxes,
            ha='left',va='top')

    # boxplots
    ax2 = fig.add_subplot(gs[1,1])
    data = []
    median_data = []
    n_data = []
    ax2.yaxis.grid()
    for k,sat in enumerate(list(np.unique(satnames))):
        idx = np.where([_ == sat for _ in satnames])[0]
        data.append(chain_error[idx])
        median_data.append(np.median(chain_error[idx]))
        n_data.append(len(chain_error[idx]))
    bp = ax2.boxplot(data,0,'k.', labels=list(np.unique(satnames)), patch_artist=True)
    for median in bp['medians']:
        median.set(color='k', linewidth=1.5)
    for j,boxes in enumerate(bp['boxes']):
        boxes.set(facecolor='C'+str(j))
        ax2.text(j+1,median_data[j]+1, '%.1f' % median_data[j], horizontalalignment='center', fontsize=12)
        ax2.text(j+1+0.35,median_data[j]+1, ('n=%.d' % int(n_data[j])), ha='center', va='center', fontsize=12,
                 rotation='vertical')
    ax2.set(ylabel='error [m]', ylim=settings['lims'])
    
    # histogram
    ax3 = fig.add_subplot(gs[1,2])
    ax3.grid(which='major',linestyle=':',color='0.5')
    ax3.axvline(x=0, ls='--', lw=1.5, color='k')
    binwidth = settings['binwidth']
    bins = np.arange(min(chain_error), max(chain_error) + binwidth, binwidth)
    density = plt.hist(chain_error, bins=bins, density=True, color='0.6', edgecolor='k', alpha=0.5)
    mu, std = stats.norm.fit(chain_error)
    pval = stats.normaltest(chain_error)[1]
    xlims = ax3.get_xlim()
    x = np.linspace(xlims[0], xlims[1], 100)
    p = stats.norm.pdf(x, mu, std)
    ax3.plot(x, p, 'r-', linewidth=1)
    ax3.set(xlabel='error [m]', ylabel='pdf', xlim=settings['lims'])
    str_stats = ' rmse = %.1f\n mean = %.1f\n std = %.1f\n q90 = %.1f' % (rmse, mean, std, q90)
    ax3.text(0, 0.98, str_stats,va='top', transform=ax3.transAxes)    
    
    return chain_sat, chain_sur, satnames, fig