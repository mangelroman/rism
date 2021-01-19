# RISM extractor

This simple python script extract incipits from [RISM](https://opac.rism.info/). 

Additionally, it converts extracted PAE incipits to Humdrum **kern and MIDI files by using paekern and hum2mid tools from [humdrum-tools](https://github.com/humdrum-tools/humdrum-tools) repository.

## Usage
1. Download XML file from [RISM](https://opac.rism.info/main-menu-/kachelmenu/data) and extract:
```
wget https://opac.rism.info/fileadmin/user_upload/lod/update/rismAllMARCXML.zip
unzip rismAllMARCXML.zip
```

2. Create a new conda environment:
```
conda env create --file=environment.yml 
```

3. Run the script:
```
python rism.py --data-dir=./output_folder --num-workers=4 rism_190118.xml
```