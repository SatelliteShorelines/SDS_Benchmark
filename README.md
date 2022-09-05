# SDS_Benchmark

This repository is a testbench for shoreline mapping algorithms using satellite imagery.

Currently there are 4 validation sites available, which are downloaded from their respective sources and processed into time-series of shoreline change along cross-shore transects:
- Narrabeen, Australia [ref](https://www.nature.com/articles/sdata201624)
- Duck, North Carolina, USA [ref](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1002/2014JC010329)
- Truc Vert, France [ref](https://www.nature.com/articles/s41597-020-00750-5#Tab2)
- Torrey Pines, California, USA [ref](https://www.nature.com/articles/s41597-019-0167-6)

The idea is that participants run their shoreline mapping algorithm at each of the sites and then we evaluate the accuracy of the satellite-derived shorelines using the in situ surveys.

[This notebook](https://github.com/kvos/SDS_Benchmark/blob/main/1_preprocess_datasets.ipynb) provides the code to download and process the publicly available shoreline datasets into time-series of shoreline change.

![image](https://user-images.githubusercontent.com/7217258/188474332-c9104f70-398b-419e-93d6-a744c2cabb2c.png)

The inputs need to run satellite-derived methods are also provided for each site:
- **Region of Interest (ROI)**: to download/crop the satellite imagery
- **Cross-shore transects**: to extract time-series of cross-shore shoreline change and apply a water level correct
- **Modelled tides**: time-series of tide levels every 5 min from the FES2014 global tide model
- **Beach slopes**: estimated from the topographic surveys, to apply a water level correction
- (**Wave parameters**): not available at the moment but can be obtained if needed

![image](https://user-images.githubusercontent.com/7217258/188473839-3a186785-79e8-4734-9d74-6dff1c7a4a71.png)

![image](https://user-images.githubusercontent.com/7217258/188474017-4131da6e-5c1a-4cca-83a1-336e6b5d57de.png)
