import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_ecg(ecg_data):
    plt.scatter(x=np.linspace(0, 1, 3000), y=ecg_data["name"][:3000], s=3)
    plt.show()


def box(data):
    sns.boxplot(np.array(data["HKQuantityTypeIdentifierHeartRate"]).astype("float"))
