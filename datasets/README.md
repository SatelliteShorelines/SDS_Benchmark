## Benchmarks datasets and input files

This folder contains all the data for testing satellite-derived shoreline mapping algorithms. Each folder contains:
- a README.md file that further describes the dataset
- `SITENAME_polygon.geojson`: a polygon showing the region of interest in WGS84 lat/long coordinates. Can be used to download/crop the satellite imagery.
- `SITENAME_transects.geojson`: cross-shore transects along which to provide the time-series of shoreline change.
- `SITENAME_reference_shoreline.geojson`: reference shoreline that can be used to seed shoreline mapping algorithms.
- `SITENAME_tides.csv`: time-series of tide levels every 5 min from the [FES2014](https://www.aviso.altimetry.fr/es/data/products/auxiliary-products/global-tide-fes/description-fes2014.html) global tide model.
- `SITENAME_waves_ERA5.csv`: time-series of deep-water wave parameters from the ERA5 reanalysis.
- `(Beach slopes)`: not available yet, will be estimated from the topographic surveys and can be used to apply a water level correction.

The information on the average beach-face slope, contour level used for the in situ shoreline timeseries, and local projection is contained in the `sites_info.txt`:

| Location    | Average Beach Slope (tanBeta)| EPSG code | Groundtruth Elevation Datum | Offset NAVD88 to MSL| MHWS contour (above MSL) |
|---------    |-------|-------|---------|----------|---------|
| NARRABEEN   | 0.1   | 28356 |  MSL    | NA       |  0.7    |
| DUCK        | 0.1   | 32119 |  NAVD88 | -0.128 m |  0.585  |
| TRUCVERT    | 0.05  | 32630 |  MSL    | NA       |  1.5    |
| TORREYPINES | 0.045 | 26946 |  NAVD88 | 0.774 m  |  0.792  |

The geospatial layers can be visualised in the QGIS file `qgis_overview.qgz` include in the repository.
