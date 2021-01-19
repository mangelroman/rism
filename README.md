# RISM extractor

This python script extracts PAE incipits from [RISM](https://opac.rism.info/) database. 

Additionally, it creates Humdrum \*\*kern and MIDI files out of the extracted incipits, using *paekern* and *hum2mid* tools from [humdrum-tools](https://github.com/humdrum-tools/humdrum-tools) repository.

## Usage
1. Download XML file from [RISM](https://opac.rism.info/main-menu-/kachelmenu/data) and decompress:
```
wget https://opac.rism.info/fileadmin/user_upload/lod/update/rismAllMARCXML.zip
unzip rismAllMARCXML.zip
```

2. Create a new conda environment based on the provided file:
```
conda env create --file=environment.yml 
```

3. Run the script (set --length to the total number of records in the XML file for progress update purposes):
```
python rism.py --data-dir=./output_folder --length=1400000 --num-workers=4 rism_201219.xml
```
