# aw40-filereader

## Install

### Initialize and activate venv
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

## Test the software
```
python main.py <Path to testfile> <optional: Format String>
```
Example:
```
python main.py test_files/picoscope.mat
```
Example for Picoscope V1:
```
python main.py test_files/1-1 "Omniscope V1 RAW"
```

## Supported File Formats
| Format            | Format String      |
| :---------------- | :----------------- |
| Picoscope: csv    | "Picoscope CSV"    |
| Picoscope: mat    | "Picoscope MAT"    |
| VCDS: txt         | "VCDS TXT"         |
| Omniscope V1: raw | "Omniscope V1 RAW" |

# Sample Output
## picscope MAT/CSV
```python
{
    'timeseries_data': [
        {
            'sampling_rate': 24414.06264837576, 
            'duration': 0.4999987169612723, 
            'signal_data': array([  
                                    0.0155034 , 
                                    -0.00225837,  
                                    0.0155034 , 
                                    ...,  
                                    0.0155034 ,
                                    0.0155034 , 
                                    0.0155034 
                                ], dtype=float32), 
            'component': 'A'
        }
     ]
}
```
## VCDS TXT
```python
{
    'vehicle': {
        'vin': 'TMBJB7NE4G0000000'
    }, 
    'case': {
        'milage': 55835
    }, 
    'obd_data': {
        'dtc_data': [
            'P1570', 
            'C102D', 
            'B10CD', 
            'B1479'
        ],
        'obd_specs': {
            'device': 'VCDS', 
            'drv_ver': '22.10.0.1', 
            'fw_ver': '0.4623.4'
        }
    }
}
```
## Omniscope V1
```python
{
    'timeseries_data': [
        {
            'signal_data': array([
                                    -0.386, 
                                    -0.394, 
                                    -0.394, 
                                    ..., 
                                    -2.014, 
                                    -2.014, 
                                    -2.006
                                ], dtype=float32), 
            'component': 'A'
        }
    ]
}
```