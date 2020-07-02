#!/usr/bin/python3
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import os


links = [0] * 3

def prob_density_fun(x, sd, avg):
    tmp = (-1 / 2) * math.pow((x - avg) / sd, 2)
    return (1 / (sd * math.sqrt(2 * math.pi)) * math.exp(tmp))

def write_to_csv(url, data):
    with open(url, "w") as fd:
        csvout = csv.writer(fd)
        for row in data:
            csvout.writerow([row[0], row[1]])

def mean_confidence_interval(data, confidence=0.90):
    print(data)
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

def analyze_data_for_mean(script, nm):
    data_tcp = [[], [], []]
    data_pareto = [[], [], []]
    means_tcp = [[], [], []]
    means_pareto = [[], [], []]

    fig, ax = plt.subplots()
    labels = []
    for i in range(0, 10):
        print("*", end=" ", flush=True)
        output = os.popen(script).read()
        x = output.splitlines()[-3:]
        for j in range(0, 3):
            t = x[j].split()
            label = ''.join(t[0:3])
            if label not in labels:
                labels.append(label)
            data_pareto[j].append(float(t[9]))
            data_tcp[j].append(float(t[11]))

    for i in range(0, 3):
        means_tcp[i] = mean_confidence_interval(data_tcp[i])
        means_pareto[i] = mean_confidence_interval(data_pareto[i])

    plot_data = [[], []]
    yerr1 = [[], []]
    
    print("PARETO: ")
    print(data_pareto)
    print("TCP: ")
    print(data_tcp)
    print("MEAN PARETO: ")
    print(means_pareto)
    print("MEAN TCP: ")
    print(means_tcp)

    ax.hist(x, align="left")
    xticks = [i for i in range(3)]
    xtick_labels = ["lien {}".format(i) for i in labels]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels)
    for i in range(0, 3):
        d1 = [means_tcp[i][0], means_pareto[i][0]]
        d2 = [means_tcp[i][1], means_pareto[i][1]]
        plot_data[0].append(d1[0])
        plot_data[1].append(d1[1])
        yerr1[0].append(d2[0])
        yerr1[1].append(d2[1])

    X = np.arange(3)
    ax.bar(X+ 0.00, plot_data[0], yerr=yerr1[0], edgecolor = 'black', capsize=7, color="g", width=0.25, label="tcp")
    ax.bar(X+ 0.25, plot_data[1], yerr=yerr1[1], edgecolor = 'black', capsize=7, color="b", width=0.25, label="on/off")
    plt.legend(loc='upper right')
    plt.savefig(nm)

"""
def read_trace(fp, links):
    charge_tcp = [0] * 3
    charge_pareto = [0] * 3
    
    data_tcp = [[]] * 3
    data_pareto = [[]] * 3
    
    last_t = float(fp.readline().split()[1])

    for i, e in enumerate(fp):
        tokens = e.split()
        link = [tokens[2], tokens[3]]
        
        if tokens[0] == '+':
            for i, e in enumerate(links):
                if link == links[i]:
                    if tokens[4] == "pareto":
                        charge_pareto[i]+=1
                        
                    if tokens[4] == "tcp":
                        charge_tcp[i]+=1   
    return charge_tcp, charge_pareto
"""
def main():
    print("DROPTAIL=> ")
    analyze_data_for_mean("./run2.sh", "droptail_50.png")
    print("RED=> ")
    analyze_data_for_mean("./run3.sh", "red_50.png")
if __name__=="__main__":
    main()
