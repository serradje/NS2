#!/usr/bin/python3
import csv
import math
import numpy as np
from scipy.stats import norm
import scipy
import matplotlib.pyplot as plt
import os

def gen_files(dire):
    directory = os.fsencode(dire)
    data20 = []
    data50 = []
    data100 = []
    names20 = []
    names50 = []
    names100 = []
    means = []
    yer1 = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith("tr"):
            tokens = filename.split('.')
            if (tokens[0][0:4] == "li50"):
                data50.append(pdf_aux("{}/{}".format(dire, filename)))
                if (tokens[0][0:5] == "li50r"):
                    names50.append("RED file 50")
                else:
                    names50.append("DT file 50")


            if (tokens[0][0:4] == "li30"):
                data20.append(pdf_aux("{}/{}".format(dire, filename)))
                if (tokens[0][0:5] == "li30r"):
                    names20.append("RED file 30")
                else:
                    names20.append("DT file 30")


            if (tokens[0][0:5] == "li100"):
                data100.append(pdf_aux("{}/{}".format(dire, filename)))
                if (tokens[0][0:6] == "li100r"):
                    names100.append("RED file 100")
                else:
                    names100.append("DT file 100")
            continue
        else:
            continue
    plt.boxplot((data20[0], data20[1], data50[0], data50[1], data100[0], data100[1]), labels=(names20[0], names20[1], names50[0], names50[1], names100[0], names100[1]))
    plt.ylabel("taille des files d'attentes")
    plt.xticks(fontsize=6, rotation=45)
    plt.savefig("test.png")

def prob_density_fun(x, sd, avg):
    tmp = (-1 / 2) * math.pow((x - avg) / sd, 2)
    return (1 / (sd * math.sqrt(2 * math.pi)) * math.exp(tmp))

def write_to_csv(url, data):
    with open(url, "w") as fd:
        csvout = csv.writer(fd)
        for row in data:
            csvout.writerow([row[0], row[1]])

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

def pdf_aux(filepath):
    fp = open(filepath)
    data = []
    for i, e in enumerate(fp):
       tokens = e.split()
       data.append(float(tokens[1]))
    return data

def plot_pdf(data, title):
    mean = np.mean(data)
    sigma = np.std(data)
    x= np.arange(-50,100,0.001)
    plt.plot(x, norm.pdf(x, mean, sigma), label=title)
    plt.legend(loc='upper left', frameon=False)

def main():
    #data1 = pdf_aux("./link_13_20.tr")
    #data2 = pdf_aux("./link_19_18.tr")
    #data3 = pdf_aux("./link_20_13.tr")
    #plt.legend(loc='upper left', frameon=False)
    #plt.boxplot((data3, data2, data1), labels=("lien 20 13", "lien 19 18", "lien 13 20"))
    #plt.show()
    gen_files("./boxplot")
    #write_to_csv("drop.dat", data)

if __name__=="__main__":
    main()
