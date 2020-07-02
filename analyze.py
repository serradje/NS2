#!/usr/bin/python3
# -*-coding:Utf-8 -*
import os

os.system("test -d tmp || mkdir tmp")
os.system("rm -f flux_*.tr lien_*.tr")

def write_to_csv(url, data):
    with open(url, "w") as fd:
        csvout = csv.writer(fd)
        for row in data:
            csvout.writerow([row[0], row[1]])


def analyze_traff(fd):
    issource = False
    pareto_global_count = {}
    pareto_global_size = {}
    tcp_global_count = {}
    tcp_global_size = {}
    tcp_flows_sent = {}
    tcp_flows_sent_size = {}
    tcp_flows_load = {}
    pareto_links_load = {}
    pareto_links_lost = {}
    tcp_links_lost = {}
    pareto_links_sent = {}
    tcp_links_load = {}
    tcp_links_sent = {}
    tcp_last_ack = {}
    tcp_flows_lost = {}
    tcp_flows_first_set = {}
    tcp_flows_first = {}

    file_lines = []
    for i, e in enumerate(fd):
        tokens = e.split()
        if (tokens[0] == '+'):
            src = tokens[8].split(".")
            issource = (src[0] == tokens[2])

            if tokens[4] == "pareto":
                if issource:
                    pareto_global_count["sent"] = pareto_global_count.get("sent", 0) + 1
                    pareto_global_size["sent"] =  pareto_global_size.get("sent", 0) + float(tokens[5])
                pareto_links_load[(tokens[2], tokens[3])] = pareto_links_load.get((tokens[2], tokens[3]), 0) + 1

            if tokens[4] == "tcp":
                if issource:
                    tcp_global_count["sent"] = tcp_global_count.get("sent", 0) + 1
                    tcp_global_size["sent"] = tcp_global_size.get("sent", 0) + float(tokens[5])
                    tcp_flows_sent[tokens[7]] = tcp_flows_sent.get(tokens[7], 0) + 1
                    tcp_flows_sent_size[tokens[7]] = tcp_flows_sent_size.get(tokens[7], 0) + float(tokens[5])
                    tcp_flows_load[tokens[7]] = tcp_flows_load.get(tokens[7], 0) + 1

                    if (tokens[7] in tcp_flows_first_set and tcp_flows_first_set[tokens[7]] != 1):
                        tcp_flows_first[tokens[7]] = float(tokens[1])
                        tcp_flows_first_set[tokens[7]] = 1
                tcp_links_load[(tokens[2], tokens[3])] = tcp_links_load.get((tokens[2], tokens[3]), 0) + 1

        if (tokens[0] == '-'):
            dst = tokens[9].split(".")
            isdest = (dst[1] == tokens[3])

            if tokens[4] == "pareto":
                pareto_links_load[(tokens[2], tokens[3])] = pareto_links_load.get((tokens[2], tokens[3]), 1) - 1
                pareto_links_sent[(tokens[2], tokens[3])] = pareto_links_sent.get((tokens[2], tokens[3]), 0) + 1

            if tokens[4] == "tcp":
                tcp_links_load[(tokens[2], tokens[3])] = tcp_links_load.get((tokens[2], tokens[3]), 1) - 1
                tcp_links_sent[(tokens[2], tokens[3])] = tcp_links_sent.get((tokens[2], tokens[3]), 0) + 1

                if (isdest):
                    tcp_flows_load[tokens[7]] = tcp_flows_load.get(tokens[7], 1) - 1
        

        if (tokens[0] == 'd'):
            if tokens[4] == "pareto":
                pareto_global_count["lost"] = pareto_global_count.get("lost", 0) + 1
                pareto_global_size["lost"] = pareto_global_size.get("lost", 0.0) + float(tokens[5])
                pareto_links_lost[(tokens[2], tokens[3])] = pareto_links_lost.get((tokens[2], tokens[3]), 0) + 1
                pareto_links_load[(tokens[2], tokens[3])] = pareto_links_load.get((tokens[2], tokens[3]), 1) - 1
            
            if tokens[4] == "tcp":
                tcp_global_count["lost"] = tcp_global_count.get("lost", 0) + 1
                tcp_global_size["lost"] = tcp_global_size.get("lost", 0) + float(tokens[5])
                tcp_flows_lost[tokens[7]] = tcp_flows_lost.get(tokens[7], 0) + 1
                tcp_flows_load[tokens[7]] = tcp_flows_load.get(tokens[7], 1) - 1
                tcp_links_lost[(tokens[2], tokens[3])] = tcp_links_lost.get((tokens[2], tokens[3]), 0) + 1
                tcp_links_load[(tokens[2], tokens[3])] = tcp_links_load.get((tokens[2], tokens[3]), 1) - 1

        if (tokens[0] == 'r'):
            dst = tokens[9].split(".")
            isdest = (dst[1] == tokens[3])
            
            if tokens[4] == "pareto":
                if (isdest):
                    pareto_global_count["received"] = pareto_global_count.get("received", 0) + 1
                    pareto_global_size["received"] = pareto_global_size.get("received", 0.0) + float(tokens[5])

            if tokens[4] == "tcp":
                if (isdest):
                    tcp_global_count["received"] = tcp_global_count.get("received", 0) + 1
                    tcp_global_size["received"] = tcp_global_size.get("received", 0.0) + float(tokens[5])
            
            if tokens[4] == "ack":
                tcp_last_ack[tokens[7]] = tokens[1]
    
    for i, e in enumerate(fd):
        tokens = e.split()
        
        key = (tokens[2], tokens[3])
        if key in  pareto_links_load and key in tcp_links_load:
            os.system("echo '{} {} {}' >> tmp/lien_{}_{}.tr".format(tokens[1], pareto_links_load[key], tcp_links_load[key], tokens[2], tokens[3]))
        if key in tcp_flows_load:
            os.system("echo '{} {}' >> tmp/flux_{}.tr".format(tokens[1], tcp_flows_load[key], tokens[7]))

    print("Taffic de fond (Pareto)")
    print("{} pacquet(s) envoyé(s)".format(pareto_global_count["sent"]))
    print("{} pacquet(s) reçu(s)".format(pareto_global_count["received"]))
    print("{} pacquet(s) perdu(s)".format(pareto_global_count["lost"]))

    print()
    print("Traffic témoin (TCP)")
    print("{} pacquet(s) envoyé(s)".format(tcp_global_count["sent"]))
    print("{} pacquet(s) reçu(s)".format(tcp_global_count["received"]))
    print("{} pacquet(s) perdu(s)".format(tcp_global_count["lost"]))


    print("Total des données transmises avec succès : {} Mo".format(((pareto_global_size["received"] + tcp_global_size["received"]) / 1000000)));
    print("Proportion de traffic de  témoin (TCP) : {} %".format(((pareto_global_size["received"] / ( pareto_global_size["received"] + tcp_global_size["received"]) * 100.0))))
    print("Proportion de traffic fond (Pareto): {}".format(((tcp_global_size["received"] / ( pareto_global_size["received"] + tcp_global_size["received"]) * 100.0))))
    print()
    print("Analyse des trois pire flux témoins :")
    print("#FLUX\tPERTES\t\t\t\tCHARGE\t\tDÉBIT UTILE")

    max_lost = 0
    index = 0

    for lim in range(0, 3):
        for i, key in enumerate(tcp_flows_lost.keys()):
            if (tcp_flows_lost[key] > max_lost):
                max_lost = tcp_flows_lost[key]
                index = key
                
        if (max_lost > 0):
            os.system("cp tmp/flux_{}.tr .".format(index))

            if (index in tcp_flows_sent and index in tcp_flows_sent and tcp_flows_sent[index] > 0):
                lost_amount_tcp = ((tcp_flows_lost[index] / tcp_flows_sent[index]) * 100)
            else:
                lost_amount_tcp = 0
                
            if (index in tcp_flows_lost and index in tcp_flows_sent and index in tcp_flows_sent_size and index in tcp_last_ack and index in tcp_flows_first):
                print(key + "\t" + lost_amount_tcp + "% ("  + tcp_flows_lost[index]  + " paquet(s))\t"  + tcp_flows_sent[index] + " paquet(s)\t" + (tcp_flows_sent_size[index] / (tcp_last_ack[index] - tcp_flows_first[index])) + " o\057s")
                
            if index in tcp_flows_lost:
                tcp_flows_lost.pop(index)
            if index in tcp_flows_sent:
                tcp_flows_sent.pop(index)
            if index in tcp_flows_load:
                tcp_flows_load.pop(index)
        max_lost = 0


    print()

    print("Analyse des trois pires liens :")
    print("LIEN\t\tPERTES ON/OFF\t\t\tPERTES TCP\t\t\tCHARGE ON/OFF\t\tCHARGE TCP")

    max_lost = 0
    index1 = 0
    index2 = 0
    lost_pareto = 0
    lost_tcp = 0 

    for lim in range(0, 3):
        for i, key in enumerate(pareto_links_lost.keys()):
            if (key in tcp_links_lost and (pareto_links_lost[key] + tcp_links_lost[key]) > max_lost):
                max_lost = tcp_links_lost[key] + pareto_links_lost[key]
                index1 = key[0]
                index2 = key[1]

        if (max_lost > 0):
            index3 = (index1, index2)
            os.system("cp tmp/lien_{}_{}.tr .".format(index1, index2))

            if (index3 in pareto_links_sent and index3 in pareto_links_lost and pareto_links_sent[index3] > 0):
                    lost_pareto = ((pareto_links_lost[index3] / pareto_links_sent[index3]) * 100)
            else:
                lost_pareto = 0

            if (index3 in tcp_links_lost and tcp_links_sent[index3] > 0):
                lost_tcp = ((tcp_links_lost[index3] / tcp_links_sent[index3]) * 100)
            else:
                lost_tcp = 0
            
            if (index3 in pareto_links_lost and index3 in tcp_links_lost and index3 in tcp_links_sent and index3 in pareto_links_sent):
                print(index1 + " --> " +  index2 +  "\t" + str(lost_pareto) + "% (" + str(pareto_links_lost[index3]) + " paquet(s))\t" + str(lost_tcp) + "% (" + str(tcp_links_lost[index3]) + " paquet(s))\t"+ str(pareto_links_sent[index3]) + " paquet(s)\t\t" + str(tcp_links_sent[index3]) + " paquet(s)")

            if index3 in pareto_links_lost:
                pareto_links_lost.pop(index3)
            if index3 in tcp_links_lost:
                tcp_links_lost.pop(index3)
            if index3 in pareto_links_sent:
                pareto_links_sent.pop(index3)
            if index3 in tcp_links_sent:
                tcp_links_sent.pop(index3)
            if index3 in pareto_links_load:
                pareto_links_load.pop(index3)
            if index3 in tcp_links_load:
                tcp_links_load.pop(index3)
        max_lost = 0

    os.system("rm -rf tmp")


fd = open("./trace.tr")
analyze_traff(fd)
