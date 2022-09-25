# Example submission

Here the submission format is described.

## Author(s)

- Yongjing Mao (The University of Queensland)

## Mapped locations

We produced shoreline time-series for the following locations (check locations):

- [x] NARRABEEN
- [x] DUCK
- [x] TRUCVERT
- [x] TORREYPINES

## Algorithm/workflow description

We used the algorithm HT-SDS as described in detail in Mao et al. (2021). The algorithm retrieved **annual** shoreline at **high tide** with image compositing methods, optimized for efficiency with the entire workflow implemented on Google Earth Engine (GEE) cloud computing platform.
The model is implemented with the GEE python API that was used here.

## Workflow to reproduce
The algorithm can be implemented for a site by simply launching
```bash
python SDSRetrieve.py --SITE SITENAME
```
To check other options to tune:
```bash
python SDSRetrieve.py -h
```

## Estimation of effort

The time it took to run the workflow was estimated below. The computation time can be substantially smaller (down to 20 sec for all sites) if a site was processed recently. The computation time in the table is based on the first-time (longest) processing.
Since the entire workflow is based on GEE, it has no requirement for client-side computational resources. 

| Location    | Download time (hrs) | Mapping time (hrs) | Total time (hrs) |
|-------------|------------------------|----------------------|------------------|
| NARRABEEN | 0                    | 0.05                   | 0.05         |
| DUCK     | 0                     |       0.05               |      0.05            |
| TRUCVERT    |	0                       |         0.1             |        0.1          |
| TORREYPINES    |	0                        |      0.15                |    0.15              |

## Additional information

This algorithm is efficiency-focused to achieven global-implementation and sacrificed accuracy in several aspects including but not limited to: (1) Use annual composites; (2) Limit the number of images processed in a year to 100; (3) Not retrieving raw images and shoreline vector.

Since all Landsat images were composited, this algorithm does not distinguish the satname for each shoreline position record.

The tidal-correction in this algorithm was achieved through image-compositing, so the water level information was not used. But it may be necessary to use this information to transform the high-tide position from this algorithm to mean sea level in order to directly compare with other algorithms
