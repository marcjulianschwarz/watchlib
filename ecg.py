import matplotlib.pyplot as plt
import numpy as np

def plot_ecg(ecg_data, meta_data=None):

    y = ecg_data["name"][:1000]
    x = np.linspace(0, 1, len(y))[:1000]

    fig, ax = plt.subplots(figsize=(10,5))
    plt.plot(x, y)

    if meta_data:
        plt.title("Date: " + meta_data["Aufzeichnungsdatum"] + "     Classification: " + meta_data["Klassifizierung"])

    plt.show()
