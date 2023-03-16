# CASSIE submission

This submission was produced with the [CASSIE](https://cassiengine.org/) open-source webtool at the benchmark sites.

## Authors

- Daniel Pais (Ciências ULisboa, Instituto Dom Luiz and +ATLANTIC)
- Luis Pedro Almeida (+ATLANTIC)

## Mapped locations

We produced shoreline time-series for the following locations:

- [x] NARRABEEN
- [x] DUCK
- [x] TRUCVERT
- [x] TORREYPINES

## Algorithm/workflow description

[CASSIE](https://cassiengine.org/) — acronym for Coastal Analyst System from Space Imagery Engine — is an open source application that uses Google Earth Engine (GEE) services to simplify and assist shoreline analysis, being able to automatically identify shoreline positions from satellite imagery and provide statistical analysis according to the Digital Shoreline Analysis System Analysis System (DSAS) specifications. The application runs entirely in a web browser and performs all the operations of high computational cost on a parallel computing platform in the GEE cloud, leaving to the user (through browser) only simple interface tasks. By accessing GEE ever-increasing dataset of satellite imagery(e.g., Landsat and Sentinel collections), [CASSIE](https://cassiengine.org/) enables to perform temporal analysis of shorelines.

[CASSIE](https://cassiengine.org/) automatically applies image mosaicking when the area of interest (AOI) intersects more than one image tile and image co-registration (correction of horizontal displacements between images). Cloud percentage over the AOI is calculated using C Function of Mask (CFMask) algorithm. Automatic shoreline detection algorithm is performed using the Normalized Difference Water Index (NDWI) whereby the image can be classified into two (water and land) or three classes (water, intertidal features, and land) depending on the inputted Otsu threshold method (respectively, 0 (default) or -1). The classified image is then vectorized into polygons and the polygon edge that first intersects with the generated transects (by drawing a landward baseline) is identified as the shoreline (the remaining polygons are ignored). The extracted shoreline is smoothed using a 1D Gaussian smoothing filter (the filter is controlled by the kernel size and the standard deviation). [CASSIE](https://cassiengine.org/) does not remove automatically outliers.

CASSIE algorithm is described in detail in [Almeida et al. 2021](https://www.researchgate.net/publication/350051153_Coastal_Analyst_System_from_Space_Imagery_Engine_CASSIE_Shoreline_management_module) and avaiable at https://cassiengine.org/ .

## Workflow to reproduce

[CASSIE](https://cassiengine.org/) is still under development, therefore some gaps in the output processing have been fulfilled outside its environment. The adopted workflow followed this order:

1. CASSIE initialization, you must have a Google account registered on the GEE platform to sign in;
2. Select the Shoreline Analyst module;
3. Select one of the available satellites for image acquisition — Sentinel (-2) or Landsat (-7, -8 and -9).
4. Choose Landsat satellite collection selection for image acquisition;
5. Draw or import (in KML format) the AOI;
6. Specify the period of analysis (maximum period available until the end of 2021) and a cloud percentage of ≤ 0%;
7. No manual filtering was applied, i.e., all selected images were included;
8. Select the Analyze Shoreline action and draw or import (in KML format) a baseline which extension must extend the AOI limits;
9. CASSIE does not allow, yet, to import transects - for this workflow we kept the default spacing and extension parameters;
10. Set an Otsu threshold of 0.01;
11. After the automatic method has finished you can visualize the satellite-derived shorelines and automatically-generated transects and subsequent statistics. Export data in shapefile format. A zip file should have been downloaded. Inside you must have, for each layer - baseline, transects and shoreline - three files (DBF, SHP and SHX). 
12. In a GIS environment (e.g., ArcGIS Pro) import the three shoreline files. Then add the information about the source coordinate system (WGS 1984) to the shapefile and transform it into the respective UTM coordinate system;
13. Finally, a simple MATLAB script for shapefile reading was built in order to achieve the intended output - the intersection point between the satellite-derived shorelines and the transects and its distance from the baseline - and create the corresponding .csv files in the SDS_Benchmark format;

## Estimation of effort

Please provide an (rough) estimate of the time it took to run the workflow (e.g., download, read in data, process). If possible, please also state the computational resources that were required.

| Location    | Download time (hrs) | Mapping time (hrs) | Total time (hrs) |
|-------------|------------------------|----------------------|------------------|
| NARRABEEN |                     |                   |          |
| DUCK     |                        |                      |                  |
| TRUCVERT    |                        |                      |                  |
| TORREYPINES    |                        |                      |                  |

## Additional information

No further manual procedures were carried out of those mentioned.
Outliers were not removed. 
Comparisons with the groundtruth data were successful.
Comparisons with different contours and different timesteps are ongoing.
