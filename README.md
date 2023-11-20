# Park Victoria project - Litter Counting

This repository is a PyTorch implementation for Litter counting project which is a AI solution for automatically counting litter in different category. Images are capture from trapboxes which are placed in various position on Yarra River, Melbourne

In this project , we advocate litter counting by regress litter densities. The base method use Context Aware Crowd Counting.
As a result, model works well on plastic bottle class due to its major occupation in our dataset. Following class is ball, helmet, etc.
We can only collected 152 images in two months of work so other class is not enough sample for model to learn.


## Installation
PyTorch 2.0

Python 3

## Dataset

&emsp;1. Download Dataset from
Google Drive: [link](https://drive.google.com/file/d/1Va48_Vphym9g8fLzeywseXhlX7VmxRWU/view?usp=sharing) 

&emsp;2. Create the hdf5 files with make_dataset.py, you need to set the path according to dataset location.

&emsp;3. Use create_json.py to generate the json file which contains the path to the images.

## Data preparing
We annotate data thank to LabelBox software.


## Training
In command line:

```
python train.py train.json val.json

``` 

The json files here are generated from previous step (Dataset. 3.)

## Tesing
&emsp;1. Modify the "test.py", make sure the path is correct.

&emsp;2. In command line:

```
python test.py

``` 

## Visualization
&emsp;1. Modify the "plot.py", make sure the path is correct.

&emsp;2. In command line:

```
python plot.py

``` 
This will plot objects density map

## Webgui Window base app

for executable file [link](https://drive.google.com/file/d/1HUmi61hAxW5O6A82jRgBkUXqjrKdtDQC/view?usp=drive_link)
or run
python run_program.py





## Contact

For any questions regard this paper/code, please directly contact [Harry Le](mailto:dzung.leanh218@gmail.com).

