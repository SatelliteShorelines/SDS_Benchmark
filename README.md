# SDS_Benchmark

This repository is a testbench for shoreline mapping algorithms using satellite imagery.

Currently there are 4 validation sites available, which are downloaded from their respective sources and processed into time-series of shoreline change along cross-shore transects:
- Narrabeen, Australia [ref](https://www.nature.com/articles/sdata201624)
- Duck, North Carolina, USA [ref](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1002/2014JC010329)
- Truc Vert, France [ref](https://www.nature.com/articles/s41597-020-00750-5#Tab2)
- Torrey Pines, California, USA [ref](https://www.nature.com/articles/s41597-019-0167-6)

The idea is that participants run their shoreline mapping algorithm at each of the sites and then we evaluate the accuracy of the satellite-derived shorelines using the in situ surveys.

[This notebook](https://github.com/kvos/SDS_Benchmark/blob/main/1_preprocess_datasets.ipynb) provides the code to download and process the publicly available shoreline datasets into time-series of shoreline change.

The inputs needed to run satellite-derived methods are also provided for each site (can be visualised by opening the QGIS file `qgis_overview.qgz`):
- **Region of Interest (ROI)**: to download/crop the satellite imagery
- **Cross-shore transects**: to extract time-series of cross-shore shoreline change and apply a water level correct
- **Modelled tides**: time-series of tide levels every 5 min from the FES2014 global tide model
- **Beach slopes**: estimated from the topographic surveys, to apply a water level correction
- (**Wave parameters**): not available at the moment but can be obtained if needed

## 1. Narrabeen, Australia, WRL dataset
![image.png](./doc/site_narrabeen.PNG)

![image](https://user-images.githubusercontent.com/7217258/188481021-470a338c-739d-4fc8-8d9e-02bfa94cd38c.png)

![image](https://user-images.githubusercontent.com/7217258/188481493-47746dbb-a4ca-4901-8932-db011a1c396d.png)

## 2. Duck, North Carolina, FRF dataset
![image.png](./doc/site_duck.PNG)

![image](https://user-images.githubusercontent.com/7217258/188481583-a711f23e-7d06-442a-a781-0346b5dde219.png)

![image](https://user-images.githubusercontent.com/7217258/188481797-1429ee75-0d4c-4969-ace7-b34c1a10d4d0.png)

## 3. Truc Vert, France, METHYS dataset
![image.png](./doc/site_trucvert.PNG)

![image](https://user-images.githubusercontent.com/7217258/188474332-c9104f70-398b-419e-93d6-a744c2cabb2c.png)

![image](https://user-images.githubusercontent.com/7217258/188474017-4131da6e-5c1a-4cca-83a1-336e6b5d57de.png)

## 4. Torrey Pines, California, Scripps dataset
![image.png](./doc/site_torreypines.PNG)

![image](https://user-images.githubusercontent.com/7217258/188481954-69a07b07-714b-4ed8-b9ea-c5991ff0d058.png)

![image](https://user-images.githubusercontent.com/7217258/188482153-8c921827-ffb1-461f-8c4b-b9d38592f1fc.png)


Work in progress:
- a notebook to evaluate the accuracy of the satellite-derived shorelines at each site
