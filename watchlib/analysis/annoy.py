from sklearn.decomposition import PCA
from annoy import AnnoyIndex
from typing import List

from watchlib.utils import ECG
from watchlib.plot import plot_ecg
from watchlib.analysis import heart_rate_variability_pairwise, bpm



# --------------------------
# Annoy
# --------------------------

def annoy_with_pca(ecgs: List[ECG], trees: int=10000) -> AnnoyIndex:

    min_features = min([len(ecg.y) for ecg in ecgs])
    components = min(len(ecgs), min_features)

    ecg_data = [ecg.y[:min_features] for ecg in ecgs]

    pca = PCA(n_components=components)
    pca.fit(ecg_data) 

    ecgs_transformed = pca.transform(ecg_data)

    t = AnnoyIndex(components, metric="angular")
    for i, ecg in enumerate(ecgs_transformed):
        t.add_item(i, ecg)
    t.build(trees)

    return t


def annoy_with_interpolation(ecgs: List[ECG], trees: int=10000, res: int=5) -> AnnoyIndex:
    
    min_features = min([len(ecg.y) for ecg in ecgs])
    
    ecg_data = [ecg.y[:min_features][::res] for ecg in ecgs]

    t = AnnoyIndex(len(ecg_data[0]), metric="angular")
    for i, ecg in enumerate(ecg_data):
        t.add_item(i, ecg)
    t.build(trees)

    return t


def annoy(ecgs: List[ECG], _from: int=None, _to: int=None, trees: int=10000) -> AnnoyIndex:

    min_features = min([len(ecg.y) for ecg in ecgs])
    
    if _from is None: _from = 0
    if _to is None: _to = min_features
    features = _to - _from

    ecg_data = [ecg.y[_from:_to] for ecg in ecgs]

    t = AnnoyIndex(features, metric="angular")
    for i, ecg in enumerate(ecg_data):
        t.add_item(i, ecg)
    t.build(trees)

    return t

def query_annoy(t: AnnoyIndex, query: int, count: int) -> List[int]:
    return t.get_nns_by_item(query, count)

def query_and_plot_annoy(t: AnnoyIndex, ecgs: List[ECG], query: int, count: int):
    items_for_0 = t.get_nns_by_item(query, count)
    for i, item in enumerate(items_for_0):
        print(item)
        print(f"BPM: {bpm(ecgs[item])} and HRV: {heart_rate_variability_pairwise(ecgs[item])}")
        if i == 0:
            plot_ecg(ecgs[item])
            continue
        plot_ecg(ecgs[item], c="r")