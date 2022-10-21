## Benchmarks datasets and input files

This folder contains all the data for testing satellite-derived shoreline mapping algorithms. Each folder contains:
- a README.md file that further describes the dataset
- `SITENAME_polygon.geojson`: a polygon showing the region of interest in WGS84 lat/long coordinates. Can be used to download/crop the satellite imagery.
- `SITENAME_transects.geojson`: cross-shore transects along which to provide the time-series of shoreline change.
- `SITENAME_reference_shoreline.geojson`: reference shoreline that can be used to seed shoreline mapping algorithms.
- `SITENAME_tides.csv`: time-series of tide levels every 5 min from the [FES2014](https://www.aviso.altimetry.fr/es/data/products/auxiliary-products/global-tide-fes/description-fes2014.html) global tide model.
- `(Beach slopes)`: not available yet, will be estimated from the topographic surveys and can be used to apply a water level correction.
- (`Wave parameters`): not available at the moment but can be obtained if needed.

The information on the average beach-face slope, contour level used for the in situ shoreline timeseries, and local projection is contained in the `sites_info.txt`:

| Location    | Average Beach Slope (tanBeta)| Contour level (above MSL) | EPSG code |
|---------    |-----|----|-------|
| NARRABEEN   | 0.1 | 0.7 | 28356 |
| DUCK        | 0.1  | 0.585 | 32119 |
| TRUCVERT    | 0.05  | 1.5 | 32630 |
| TORREYPINES | 0.045 | 0.792 | 26946 |

The geospatial layers can be visualised in the QGIS file `qgis_overview.qgz` include in the repository.
