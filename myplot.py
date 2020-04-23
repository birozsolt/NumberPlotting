import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import brentq
from sklearn import metrics
import itertools


def calculate_roc_auc(digitdata, digit):
    labels = digitdata['label']
    scores = digitdata['score']
    labels = [int(e) for e in labels]
    scores = [float(e) for e in scores]
    scores = [1 / (1 + e) for e in scores]

    auc_value = metrics.roc_auc_score(np.array(labels), np.array(scores))

    fpr, tpr, thresholds_no = metrics.roc_curve(labels, scores, pos_label=1)
    eer = brentq(lambda x: 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    print("Digit " + str(digit) + " AUC:" + str(auc_value) + " EER:" + str(eer * 100) + "%")
    return eer * 100, auc_value, fpr, tpr


def plot_roc(digit_data, digit, result_type):
    eer, auc_value, fpr, tpr = calculate_roc_auc(digit_data, digit)
    fpr = [i * 50 for i in fpr]
    tpr = [i * 50 for i in tpr]
    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='black', lw=lw, label='AUC = %0.4f, EER= %0.4f' % (auc_value, eer))
    plt.plot([0, 50], [0, 50], color='darkorange', lw=lw, linestyle='--')
    plt.xlim([0.0, 50.0])
    plt.ylim([0.0, 50.5])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC digit ' + str(digit) + ' (' + result_type.name + ')')
    plt.legend(loc="lower right")
    plt.show()


def plot_fig(eer, numbers, result_type):
    plt.figure()
    plt.plot(numbers, eer, 'ro-', label='EER0 = %0.4f, EER9= %0.4f' % (eer[0], eer[9]))
    plt.xlabel('Number of digits of the password')
    plt.ylabel('EER value (%)')
    plt.xlim([0, 9])
    plt.ylim([0, 50])
    plt.title('System performance in terms of EER' + '(' + result_type.name + ')')
    plt.legend(loc="lower right")
    plt.show()


def run_password_length_test(filename, result_type):
    data = pd.read_csv(filename)

    for digit in range(0, 10):
        digit_data = data[data['digit'] == digit]
        plot_roc(digit_data, digit, result_type)

    system_eer = []
    combination_eer = []

    for length in range(1, 11):
        combinations = list(itertools.combinations(range(10), length))
        combination_eer.clear()
        for tuple in combinations:
            digit_data = data.loc[data['digit'].isin(list(tuple))]
            eer, auc_value, fpr, tpr = calculate_roc_auc(digit_data, ''.join(str(x) for x in tuple))
            combination_eer.append(eer)

        system_eer.append(sum(combination_eer) / len(combinations))
        print(length, sum(combination_eer) / len(combinations))

    plot_fig(system_eer, range(10), result_type)
