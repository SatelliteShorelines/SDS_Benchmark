# Deltatares submission

This submission was produced with the Deltares in-house automated Satellite Derived Shorelines (SDS) scripts at all benchmark sites.

## Author(s)

- Etiënne Kras (Deltares)
- Arjen Luijendijk (Deltares, TU Delft)
- Floris Calkoen (Deltares, TU Delft)

## Mapped locations

We produced shoreline time-series for the following locations (check locations):

- [x] NARRABEEN
- [x] DUCK
- [x] TRUCVERT
- [x] TORREYPINES

## Algorithm/workflow description

We used the algorithm as described in detail in Luijendijk et al. (2018). The algorithm retrieves images from the Landsat archives (L5, 7 & 8) and creates annual composites with a fixed yearly or moving average monthly time window and a maximum cloud cover threshold of 75%. The average water level is MSL with enough images available in the composite. The algorithm makes use of the Google Earth Engine (GEE) cloud computing platform for various calculations. The shoreline is computed by means of the NDWI and its optimal Otsu threshold to seperate between land and water. 

## Workflow to reproduce

Workflow is Deltares internal and is not shared.

## Estimation of effort

Please provide an (rough) estimate of the time it took to run the workflow (e.g., download, read in data, process). If possible, please also state the computational resources that were required. This is not tracked, but can be in later iterations for both fixed annual and movingaverage monthly shorelines. For now, we expect this to be in the same order as the CoastSat toolbox for moving average monthly shorelines.

| Location    | Download time (mins) | Mapping time (mins) | Total time (hrs) |
|-------------|------------------------|----------------------|------------------|
| NARRABEEN |                     |                    |          |
| DUCK     |                        |                      |                  |
| TRUCVERT    |                        |                      |                  |
| TORREYPINES    |                        |                      |                  |

## Additional information

As shorelines are computed are computed using composites (with MSL being the reference level), they should be compared to survey data contours equalling 0 m. Both fixed timestep annual composite as well as moving average monthly estimates are provided, the latter allows to compute HR shorelines using the composite method. Both the raw and cleaned shoreline positions are provided in CSV files. Here, outliers (as example, 3 points for Narrabeen for both monthly and yearly data) are omitted for the cleaned CSV files using inhouse outlier detection algorithms. Since all Landsat images were composited, this algorithm does not distinguish the “satname” as an individual column in output files.
