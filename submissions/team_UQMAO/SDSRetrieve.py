# -*- coding: utf-8 -*-
"""
This script performs GEE-based SDS at high tide
It retrieves annual high-tide shoreline positions along transects

"""

import os
import argparse
import time
import geojson
import pandas as pd
import ee
ee.Initialize()


def getCmdargs():
    """
    Define inputs from commandline arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--SITE",
                   help="Name of state (default=%(default)s)")
    p.add_argument("--SYEAR", type=int, default=1984,
                   help="Start year of the analysis")
    p.add_argument("--EYEAR", type=int, default=2021,
                   help="End year of the analysis")
    p.add_argument("--INDIR", default="../../datasets",
                   help="Directory for input files")
    p.add_argument("--OUTDIR", default="",
                   help="Directory for output files")
    p.add_argument("--IMGLIMIT", type=int, default=100,
                   help="Limit for the number of images used in a year")

    cmdargs = p.parse_args()
    return cmdargs


def mainRoutine():
    cmdargs = getCmdargs()

    MISSIONS = ['L5', 'L7', 'L8']  # Image sources to be included
    START_YEAR = cmdargs.SYEAR  # Starting date of analysis
    END_YEAR = cmdargs.EYEAR  # Ending date of analysis
    SITE = cmdargs.SITE
    INPUT_DIR = cmdargs.INDIR
    OUTPUT_DIR = cmdargs.OUTDIR

    ANNUAL_IMAGE_LIMIT = 100  # Limit for the number of images used in a year

    """
    Read AOI and transects and convert to GEE geometries
    """

    # Read AOI
    with open(os.path.join(
            INPUT_DIR, SITE, '{}_polygon.geojson'.format(SITE))
            ) as f:
        AOI_json = geojson.load(f)
        # Remove the third dimension in coords
        AOI_ZCoords = AOI_json['features'][0]['geometry']['coordinates'][0]
        AOI_coords = [coord[0:2] for coord in AOI_ZCoords]
        AOI_ee = ee.Geometry.Polygon(AOI_coords)

    # Read transects
    with open(os.path.join(
            INPUT_DIR, SITE, '{}_transects.geojson'.format(SITE))
            ) as f:
        transect_features = geojson.load(f)['features']
        # Add a property of feature NO as numerical value
        # starting from 1 for raster conversion
        transect_names = []
        transect_Nos = range(1, len(transect_features)+1)
        for i in transect_Nos:
            transect_features[i-1]['properties']['ID'] = i
            transect_names.append(transect_features[i-1]['properties']['name'])
        transects_ee = ee.FeatureCollection(transect_features)

    """
    Filter image collections
    """

    # Optical image collection
    collection_ids = {
        'L5': "LANDSAT/LT05/C01/T1_SR",
        'L7': "LANDSAT/LE07/C01/T1_SR",
        'L8': "LANDSAT/LC08/C01/T1_SR"
    }

    # Optical bands used to calculate AWEI
    optical_bands = {
        'L5': ['B1', 'B2', 'B4', 'B5', 'B7'],
        'L7': ['B1', 'B2', 'B4', 'B5', 'B7'],
        'L8': ['B2', 'B3', 'B5', 'B6', 'B7']
    }

    # Merge collections
    for mission in MISSIONS:
        collection = ee.ImageCollection(
            collection_ids[mission]).filterBounds(AOI_ee).select(
                optical_bands[mission], ['B', 'G', 'NIR', 'SWIR1', 'SWIR2']
                ).sort('CLOUD_COVER')
        if mission == MISSIONS[0]:
            collections = collection
        else:
            collections = collections.merge(collection)

    '''
    Retrive and save data
    '''
    years = range(START_YEAR, END_YEAR+1)
    df = pd.DataFrame(columns=transect_names, index=years)
    stime = time.time()

    for year in years:
        print('Processing {}'.format(year))
        try:
            positions = retrieve_SDS(year, collections, ANNUAL_IMAGE_LIMIT,
                                     AOI_ee, transects_ee)

            df.loc[year, positions.keys()] = list(positions.values())
        except ee.ee_exception.EEException:
            time.sleep(10)

    # Save data
    df = df.loc[~(df == -9999).any(1)]
    dest_dir = os.path.join(OUTPUT_DIR, SITE)
    if not os.path.exists(dest_dir):
        os.mkdir(os.path.join(dest_dir))

    for column in df.columns:
        df_transect = pd.DataFrame(
            {'Date': pd.to_datetime(df.index.astype(str)),
             'Distance': df[column]})
        df_transect.to_csv(os.path.join(dest_dir, '{}.csv'.format(column)),
                           index=False)

    etime = time.time()
    print('Time used: {}'.format(etime-stime))


def smooth(image):
    return image.resample('bicubic')


def retrieve_SDS(year, collections, limit, AOI, transects):
    """
    This function retrive shoreline position
    """
    # Mask terrain shadows with HydroSHEDs and HAND data
    hydrosheds = ee.Terrain.slope(
        ee.Image('WWF/HydroSHEDS/03CONDEM')
        ).clip(AOI)
    HAND = ee.Image("MERIT/Hydro/v1_0_1").select('hnd').clip(AOI)
    m_shadow = hydrosheds.gt(5)
    f_shadow = HAND.gt(30)
    shadow = f_shadow.Or(m_shadow).clip(AOI)

    # Filter yearly images, use a limit number of most clear images
    sdate = str(year)+'-01-01'
    edate = str(year+1)+'-01-01'
    maincol = collections.filterDate(sdate, edate).limit(
        limit, 'CLOUD_COVER').map(smooth)

    # Composite images with 10th percentile to get clear and high tide image
    composite = maincol.reduce(ee.Reducer.percentile([10])).select(
        ['B_p10', 'G_p10', 'NIR_p10', 'SWIR1_p10', 'SWIR2_p10'],
        ['B', 'G', 'NIR', 'SWIR1', 'SWIR2']).clip(AOI)

    # Calculate AWEI noshadow
    AWEI_nsh = (composite.select('G').subtract(composite.select('SWIR1'))
                ).multiply(4).subtract(
                    composite.select('NIR').multiply(0.25).add(
                        composite.select('SWIR2').multiply(2.75)))

    # Thresholding AWEI to get land image including shadow
    Land_nsh = AWEI_nsh.lt(0)
    shadow = shadow.unmask(0)
    Land = Land_nsh.Or(shadow)
    Land = Land.updateMask(Land)

    # Create an pixel area image to cover land area for position calculation
    pixel_area_land = ee.Image.pixelArea().updateMask(Land)

    # Get intersection length between transect and land
    transects_length = pixel_area_land.reduceRegions(
        transects, ee.Reducer.sum(), 1
        ).aggregate_array('sum')

    transects_ID = transects.aggregate_array('name')

    # Only results from composites with > 5 images were considered valid
    positions = ee.Algorithms.If(
        maincol.size().gt(5),
        transects_length,
        ee.List.repeat(-9999, transects.size()))

    positions_dict = ee.Dictionary.fromLists(
        transects_ID, positions).getInfo()

    return (positions_dict)


if __name__ == "__main__":
    mainRoutine()
