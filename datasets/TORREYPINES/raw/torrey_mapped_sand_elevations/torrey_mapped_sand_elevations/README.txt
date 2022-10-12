README file for "torrey_mapped_sand_elevations" folder of 
Ludka BC, Guza RT, O’Reilly WC, Merrifield MA, Flick RE, Bak S, Hesser TJ, Bucciarelli RL, Olfe C, Woodward B, Boyd W, Smith K, Okihiro M, Grenzeback R, Parry L, Boyd G. Data from: Sixteen years of bathymetry and waves at San Diego Beaches. Dryad Digital Repository. 

For more information, refer to Ludka BC, Guza RT, O’Reilly WC, Merrifield MA, Flick RE, Bak S, Hesser TJ, Bucciarelli RL, Olfe C, Woodward B, Boyd W, Smith K, Okihiro M, Grenzeback R, Parry L, Boyd G. (2019) Sixteen years of bathymetry and waves at San Diego Beaches, Scientific Data.

-----

EXAMPLE FILE:

Format:
           netcdf4_classic
Global Attributes:
           title                    = 'Mapped sand level elevations at Torrey Pines Beach'
           summary                  = 'Maps are created on the same grid as the binned observations (see `gridID` global attribute), but are smoothed and fill in small data gaps. Only grid points with more than `countbinThresh` data points are considered sampled. Map boundaries are defined as grid points that are regularly sampled during unnourished full surveys that span all regions (must be populated at least `fullcountFrac` as many times as the most frequently full surveyed grid point, during times without nourishment). Grid points with an average depth greater than 8m are not mapped because speed of sound errors due to stratification may contaminate jetski sonar measurements. Cross- and alongshore gaussian length scales (`Lx`,`Ly`), and `noise_var` parameters used in the mapping are listed as global attributes. `Lx` has units of meters, `noise_var` has units of meters^2, and `Ly` has units of binning transect number. The length scales were chosen such that the observations are generally smooth over these distances but sharp features may be obscured. Map errors become large where gaps in the data are larger than these length scales, therefore mapped data is thrown out where the normalized mean square error estimate (nmseEst) exceeds `errThresh`. The error estimates provided by the mapping technique were found not representative of true errors, however the estimates provide qualitative guidance of the distance of grid points from observations.'
           source                   = 'Computed using Matlab code: maps.m'
           processing_level         = 'mapped'
           gridID                   = 'mop100crs5'
           countbinThresh           = 2
           fullcountFrac            = 0.25
           mapID                    = 'guassian_Lx15_Ly2_noise0pt02'
           Lx                       = 15
           Ly                       = 2
           noise_var                = 0.02
           errThresh                = 0.2
           Conventions              = 'CF-1.6'
           standard_name_vocabulary = 'CF Standard Name Table v64'
           keywords                 = 'Earth Science > Oceans > Coastal Processes > Shoreline / Beaches / elevation / sediment transport'
           history                  = 'version1_20190407'
           corresponding_author     = 'Bonnie Ludka'
           contact                  = 'bludka@ucsd.edu'
           references               = 'Sixteen years of bathymetry and waves at San Diego beaches, Ludka et al. (2019), Scientific Data AND Dryad Repository'
           institution              = 'Scripps Institution of Oceanography'
           date_created             = '20190407'
           comment                  = 'Refer to Ludka et al. (2019), Scientific Data, for more information'
           acknowledgement          = 'This study was funded by the United States Army Corps of
                                       Engineers (W912HZ-14-2-0025) and the California Department of Parks and Recreation,
                                       Division of Boating and Waterways Oceanography Program (C1370032). Additional 
                                      support was provided by California Sea Grant, the Southern California Coastal Ocean 
                                      Observing System, the Office of Naval Research, and the California Ocean Protection 
                                      Council. Thanks to many who made this work possible; lifeguards, surfers, 
                                      city managers, SIO administrators, and supportive partners.'
Dimensions:
           alongshoreCoord = 79
           crossshoreCoord = 146
Variables:
    mapz          
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue              = -99999
                       long_name               = 'mapped (smoothed and interpolated) elevation'
                       standard_name           = 'height_above_geopotential_datum'
                       units                   = 'm'
                       positive                = 'up'
                       geopotential_datum_name = 'NAVD88 GEOID99, epoch 2002'
                       comment                 = 'Used in combination with nmseEst. Values flagged as missing when nmseEst>errThresh'
                       valid_max               = 5.1432
                       valid_min               = -7.8999
    nmseEst       
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue = -99999
                       long_name  = 'Normalized mean square error (NMSE) estimate from interpolation'
                       comment    = 'NMSE>0.2 typically considered inaccurate'
                       valid_max  = 0.37792
                       valid_min  = 0.0061804
    mapfluc       
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue = -99999
                       long_name  = 'mapped (smoothed and interpolated) elevation fluctuation'
                       units      = 'm'
                       comment    = 'mapz = mapfluc + zmeanInt. Used in combination with nmseEst. Values flagged as missing when nmseEst>errThresh'
                       valid_max  = 1.2676
                       valid_min  = -2.1107
    zmeanInt      
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue              = -99999
                       long_name               = 'mapped (smoothed and interpolated) time-averaged spatially-varying mean elevation'
                       standard_name           = 'height_above_geopotential_datum'
                       units                   = 'm'
                       positive                = 'up'
                       geopotential_datum_name = 'NAVD88 GEOID99, epoch 2002'
                       valid_max               = 4.0995
                       valid_min               = -7.3645
    nmseEstForMean
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue = -99999
                       long_name  = 'Normalized mean square error (NMSE) estimate for mapped mean surface'
                       comment    = 'NMSE>0.2 typically considered inaccurate'
                       valid_max  = 0.073167
                       valid_min  = 1.3366e-05
    xc            
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name                        = 'easting (UTM Zone 11) coordinates of grid bin centers'
                       standard_name                    = 'projection_x_coordinate'
                       units                            = 'm'
                       projected_coordinate_system_name = 'UTM Zone 11'
                       horizontal_datum_name            = 'NAD83 CORS96, epoch 2002, ellipsoid GRS80'
    yc            
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name                        = 'northing (UTM Zone 11) coordinates of grid bin centers'
                       standard_name                    = 'projection_y_coordinate'
                       units                            = 'm'
                       projected_coordinate_system_name = 'UTM Zone 11'
                       horizontal_datum_name            = 'NAD83 CORS96, epoch 2002, ellipsoid GRS80'
    latc          
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name             = 'latitude coordinates of grid bin centers'
                       standard_name         = 'latitude'
                       units                 = 'degrees_north'
                       horizontal_datum_name = 'NAD83 CORS96, epoch 2002, ellipsoid GRS80'
    lonc          
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name             = 'longitude coordinates of grid bin centers'
                       standard_name         = 'longitude'
                       units                 = 'degrees_east'
                       horizontal_datum_name = 'NAD83 CORS96, epoch 2002, ellipsoid GRS80'
    crs           
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name = 'cross-shore location relative to estimated mean shoreline position'
                       units     = 'm'
    alg           
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       long_name = 'alongshore location defined by MOP index number'
    tbinMedian    
           Size:       79x146
           Dimensions: alongshoreCoord,crossshoreCoord
           Datatype:   double
           Attributes:
                       _FillValue    = -99999
                       long_name     = 'median UTC time value in bin'
                       standard_name = 'time'
                       units         = 'seconds since 1970-01-01 00:00:00 0:00'
                       valid_max     = 1475102178.36
                       valid_min     = 1474957481.58