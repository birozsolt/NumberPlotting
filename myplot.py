import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import brentq
from sklearn import model_selection, metrics


def plot_roc(digitdata, digit, result_type):
    labels = digitdata['label']
    scores = digitdata['score']
    # print(labels.shape)
    labels = [int(e) for e in labels]
    scores = [float(e) for e in scores]
    scores = [1 / (1 + e) for e in scores]

    auc_value = metrics.roc_auc_score(np.array(labels), np.array(scores))

    fpr, tpr, thresholds_no = metrics.roc_curve(labels, scores, pos_label=1)
    eer = brentq(lambda x: 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    print("Digit " + str(digit) + " AUC:" + str(auc_value) + " EER:" + str(eer))

    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='black', lw=lw, label='AUC = %0.4f, EER= %0.4f' % (auc_value, eer))
    plt.plot([0, 1], [0, 1], color='darkorange', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC digit ' + str(digit) + ' (' + result_type.name + ')')
    plt.legend(loc="lower right")
    plt.show()


# main
def run(filename, type):
    data = pd.read_csv(filename)
    print(data.shape)
    plot_roc(data, 1234567890, type)
    for digit in range(0, 10):
        digitdata = data[data['digit'] == digit]
        plot_roc(digitdata, digit, type)
