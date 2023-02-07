All data have been procesed using these parameters:

contour_dict = {'NARRABEEN':  {'MSL':  0,  'MHWS': 0.700,    'SLOPE': 0.1}, # survey datum is MSL
                'DUCK':       {'MSL':  0,  'MHWS': 0.585,  'SLOPE': 0.1}, # survey datum is NAVD88
                'TRUCVERT':   {'MSL':  0,  'MHWS': 1.500,    'SLOPE': 0.05}, # survey datum is MSL
                'TORREYPINES':{'MSL':  0,  'MHWS': 0.792,  'SLOPE': 0.045}, # survey datum is NAVD88
               }

The folder structure is organised as follows:

- SITE NAME

	- PROFILES_COMPARISON: shorelines compared against the profiles (shp files)

		- SHORELINES: shp files with date and time in the database
		- F_RAW_TIMESERIES: raw csv files filtered to avoid outliers
		- F_TIDALLY_CORRECTED_TIMESERIES_MHWS: raw csv files corrected by MHWS and filtered to avoid outliers
		- F_TIDALLY_CORRECTED_TIMESERIES_MSL: raw csv files corrected by MSL and filtered to avoid outliers
		- EVALUATION_F_RAW_TIMESERIES_MHWS: evaluation for csv files in F_RAW_TIMESERIES folder using MHWS as reference
		- EVALUATION_F_RAW_TIMESERIES_MSL: evaluation for csv files in F_RAW_TIMESERIES folder using MSL as reference
		- EVALUATION_F_TIDALLY_CORRECTED_TIMESERIES_MHWS: evaluation for csv files in F_TIDALLY_CORRECTED_TIMESERIES_MHWS folder using MHWS as reference
		- EVALUATION_F_TIDALLY_CORRECTED_TIMESERIES_MSL: evaluation for csv files in F_TIDALLY_CORRECTED_TIMESERIES_MSL folder using MSL as reference

	- REMAINING_SHORELINES: shp files for the whole period (1984-2022) except the period of the profiles survey (in the folder PROFILES_COMPARISON).
				Each shp file contains date and time in the database.
		
** IMPORTANT NOTE: TRUCVERT data corresponds to those dates where the tidal level is higher than 0.2m (MSL)