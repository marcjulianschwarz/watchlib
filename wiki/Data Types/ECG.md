> class watchlib.utils.ECG

This is the data type for all ECGs. You can use it to access metadata and the data itself of an ECG.

```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
ecgs = dl.load_ecgs()
ecgs = ecgs[0]

ecg.meta_data # -> dictionary containing all metadata
ecg. # or route.speed -> pd.Series with speed data 
```

## Parameters:
- **data** : List[float]
- **name** : str

## Properties:
- **route** : pd.DataFrame
- **meta_data** : Dict[str:str]
- **name** : str
- **x**: List[int]
- **y**: List[float]

Properties in *meta_data* can be accessed like this:

```python
ecg["key"]
```

where `key` is a valid key. These keys are in the Apple Watch users native language.