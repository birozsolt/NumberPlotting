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
    return eer


def plot_fig(eer, numbers, type):
    plt.figure()
    plt.plot(numbers, eer, 'ro-', label='EER1 = %0.4f, EER9= %0.4f' % (max(eer), min(eer)))
    plt.xlabel('Number of digits of the password')
    plt.ylabel('EER value (%)')
    plt.xlim([0, 9])
    plt.ylim([min(eer) - 5, max(eer) + 5])
    plt.title('System performance in terms of EER' + '(' + type.name + ')')
    plt.legend(loc="lower right")
    plt.show()


# main
def run(filename, type):
    data = pd.read_csv(filename)
    # print(data.shape)
    digitarray = []
    eerarray = []
    digitarray.append(0)
    string = str(0)
    digitdata = data[data['digit'] == 0]
    eerarray.append(plot_roc(digitdata, string, type))
    for digit in range(1, 10):
        digitarray.append(digit)
        digitdata = data.loc[data['digit'].isin(digitarray)]
        string += str(digit)
        eerarray.append(plot_roc(digitdata, string, type))

    plot_fig([i * 100 for i in eerarray], digitarray, type)