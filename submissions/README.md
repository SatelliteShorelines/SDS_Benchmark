# Shoreline results

This folder contains the shoreline change time-series from the different participating teams.

## Format of the outputs

An example of submission is provided in the `example_submission` folder. There is one folder per site and in that folder the shoreline time-series are separated in two subfolders:
- `raw_timeseries`: contains the raw time-series of shoreline change along the transects, as extracted from the images (no water level correction).
- `tidally_timeseries`: contains the tidally-corrected shoreline change time-series along the transects (can also include a wave correction).

**The format of the time-series is one .csv file per transect**, named with the following convention `PROFILENAME_timeseries_raw.csv` and `PROFILENAME_timeseries_tidally_corrected.csv` where:
- the first column contains the date in UTC time
- the second column contains the cross-shore distance of the shoreline from the origin of the transect
- the third column is optional and contains the name of the satellite mission from which the datapoint was extracted

![image](https://user-images.githubusercontent.com/7217258/191886739-9a5403a9-d599-4e63-8281-a9a9e7723f58.png)

An example of csv file is provided for Narrabeen under `/submissions/example_submission/NARRABEEN`.

## How to submit

To submit your results, please:

1. [fork](https://github.com/SatelliteShorelines/SDS_Benchmark/fork) this repository;
2. Copy the `example_submission` folder and rename (e.g., 'team_CoastSat');
3. Change the files in the folder and fill the README.md file;
4. Create a [Pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) to the original repository to submit your results.

If you need any help with this submission, please post in the [GitHub Issues](https://github.com/SatelliteShorelines/SDS_Benchmark/issues) page.
