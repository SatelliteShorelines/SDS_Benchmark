## Benchmarks datasets and input files

This folder contains all the data for testing satellite-derived shoreline mapping algorithms. Each folder contains:
- a README.md file that further describes the dataset
- `SITENAME_polygon.geojson`: a polygon showing the region of interest in WGS84 lat/long coordinates. Can be used to download/crop the satellite imagery.
- `SITENAME_transects.geojson`: cross-shore transects along which to provide the time-series of shoreline change.
- `SITENAME_reference_shoreline.geojson`: reference shoreline that can be used to seed shoreline mapping algorithms.
- `SITENAME_tides.csv`: time-series of tide levels every 5 min from the [FES2014](https://www.aviso.altimetry.fr/es/data/products/auxiliary-products/global-tide-fes/description-fes2014.html) global tide model.
- (`Beach slopes`): estimated from the topographic surveys, can be used to apply a water level correction
- (`Wave parameters`): not available at the moment but can be obtained if needed

The information on the average beach-face slope and countour level used for the in situ shoreline timeseries is contained in the `sites_info.txt`.

The geospatial layers can be visualised in the QGIS file `qgis_overview.qgz` include in the repository.

