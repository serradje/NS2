#!/usr/bin/python3
# -*-coding:Utf-8 -*

import scipy.special as sps
import random as rand
import math
import sys
import numpy

# Fonction qui permet de générer le code tcl en extrayant les données dans le fichier topo.top
def Simulation(topo,output) :
   #stockages des noeuds
    nodes = []
   #parcours ligne par ligne du fichier d'entree
    for line in topo :
        lu = line.strip()
        if not lu :
            continue
        else :
            data = lu.split(' ')
            src = data[0]
            dst = data[1]
            bandwidth = data[2]
            delay = data[3]

           	#on verifie si les noeuds existent deja ou non
            if src not in nodes :
                output.write("set n(%s) [$ns node]\n" %(src))
                nodes.append(src)

            if dst not in nodes :
                output.write("set n(%s) [$ns node]\n" %(dst))
                nodes.append(dst)

            #gestion des liens
            output.write("$ns duplex-link $n(%s) $n(%s) %sMb %sms DropTail\n" %(src, dst, bandwidth, delay))

            # gestion de la file d'attente
            output.write("$ns queue-limit $n(%s) $n(%s) 20\n" %(src, dst))
    return


# Fonction qui permet de générer le traffic à injecter sur les liens en extrayant les données dans le fichier traff.traf
def GenerationTraffic(traff,output):
    # On fixe les paramètres de la distribution de pareto et loi de zipf.
		# burst et idle permettent de déinir les périodes ON/OFF,le shape,
		# ou rayon de courbure,il va permettre de controler le nombre de flux souris et éléphants
		#date de début et de fin pour lapplication qui génére le trafic de Pareto
    dateDebut = 300.0 * 0.05
    dateFin = 300.0 * 1.05

    # nombres de flux TCP temoins généré
    nb_flux_tcp = 0

    # Parcours ligne par ligne du fichier d'entree
    for line in traff :
        lu = line.strip()
        if lu :
           	#découpage de la ligne lue en champs src,dst et volume
            data = lu.split(' ')
            src = data[0]
            dst = data[1]
            volume = float(data[2])

            volumeOn_off = volume * 0.80
            volumeTCP = volume * (1.0 - 0.80)

            #génération du traffic de type ON/OFF
            portionBurst = (0.5 / 1) * 100.0
            volumeAenvoyer = volumeOn_off * (100.0 / portionBurst)
  
            if volumeAenvoyer < 300.0 :
                rate = volumeAenvoyer
                dateFin = dateDebut + 1
            else :
                rate = volumeAenvoyer / 300.0
                dateFin = 300.0 * 1.05

           	#Creation des agents UDP d'envoi et de reception
						#Attachement des agents crees aux noeuds correspondants
						#Etablissement de la connexion entre les agents
            output.write("set udp_sender(%s.%s) [new Agent/UDP]\n" %(src, dst))
            output.write("set udp_receiver(%s.%s) [new Agent/Null]\n" %(src, dst))
            
            output.write("$ns attach-agent $n(%s) $udp_sender(%s.%s)\n" %(src, src, dst))
            output.write("$ns attach-agent $n(%s) $udp_receiver(%s.%s)\n" %(dst, src, dst))

            output.write("$ns connect $udp_sender(%s.%s) $udp_receiver(%s.%s)\n" %(src, dst, src, dst))

            output.write("set pareto_app(%s.%s) [new Application/Traffic/Pareto]\n" %(src, dst))
            output.write("$pareto_app(%s.%s) set burst_time_ %ss\n" %(src, dst, 0.5))
            output.write("$pareto_app(%s.%s) set idle_time_ %ss\n" %(src, dst, 0.5))
            output.write("$pareto_app(%s.%s) set rate_ %f\n" %(src, dst, (rate * 8)))
            output.write("$pareto_app(%s.%s) set packetSize_ %s\n" %(src, dst, 1500))
            output.write("$pareto_app(%s.%s) set shape_ %s\n" %(src, dst, 1.2))
            output.write("$pareto_app(%s.%s) attach-agent $udp_sender(%s.%s)\n" %(src, dst, src, dst))

            output.write("$ns at %s \"$pareto_app(%s.%s) start\"\n" %(dateDebut, src, dst))
            output.write("$ns at %s \"$pareto_app(%s.%s) stop\"\n" %(dateFin, src, dst))

            #génération du traffic tcp témoins:
             #le volume de donnees est générer aleatoirement suivant la loi de Zipf:
            volumeTrafficTcp = 0.0
            while volumeTrafficTcp < volumeTCP :  
                                    
                a = 1.0698
                volumeFlux = numpy.random.zipf(a, 1)[0]

                        #si on depasse le volume généré
                if (volumeTrafficTcp + volumeFlux) > volumeTCP:
                    volumeFlux = volumeTCP - volumeTrafficTcp

                #en utilisant la loi de poisson, on génere une date aléatoire de début de flux
                debutDeFlux = numpy.random.poisson(300.0 / 2, 1)[0]

                        #si on dépasse la durée de simulation.
                if debutDeFlux > 300.0 :
                    debutDeFlux = 0.8 * dateFin

                #Creation des agents TCP d'envoi et de reception
                #Attachement des agents crees aux noeuds correspondants
                #Etablissement de la connexion entre les agents
                output.write("set tcp_sender(%s.%s.%s) [new Agent/TCP]\n" %(src, dst, nb_flux_tcp))
                output.write("$tcp_sender(%s.%s.%s) set packetSize_ %s\n" %(src, dst, nb_flux_tcp, 1500))
                output.write("$tcp_sender(%s.%s.%s) set fid_ %s\n" %(src, dst, nb_flux_tcp, nb_flux_tcp))

                output.write("set tcp_receiver(%s.%s.%s) [new Agent/TCPSink]\n" %(src, dst, nb_flux_tcp))
                output.write("$ns attach-agent $n(%s) $tcp_sender(%s.%s.%s)\n" %(src, src, dst, nb_flux_tcp))
                output.write("$ns attach-agent $n(%s) $tcp_receiver(%s.%s.%s)\n" %(dst, src, dst, nb_flux_tcp))

                output.write("$ns connect $tcp_sender(%s.%s.%s) $tcp_receiver(%s.%s.%s)\n" %(src, dst, nb_flux_tcp, src, dst, nb_flux_tcp))
                output.write("$ns at %s \"$tcp_sender(%s.%s.%s) send %s\"\n" %(debutDeFlux, src, dst, nb_flux_tcp, int(volumeFlux)))
                
                volumeTrafficTcp += volumeFlux
                nb_flux_tcp += 1
    print("%s flux temoin(s) generes" %(nb_flux_tcp))
    return

# on ouvre les différents fichiers
topo = open(sys.argv[1], "r");
traff = open(sys.argv[2], "r");
output = open("simulation.tcl", "w");

# Début et fin du script Tcl généré
header = """
set ns [new Simulator]
set nf [open out.nam w]
$ns namtrace-all $nf
set tf [open trace.tr w]
$ns trace-all $tf
set f [open congestion.tr w]

proc finish {} {
  global ns nf tf
  $ns flush-trace
  close $tf
  exec nam -a out.nam &
  puts "Simulation Terminée."
  exit 0
}

proc plotWindow {tcpSource fichier} {
global ns
set time 0.1
set now [$ns now]
set cwnd [$tcpSource set cwnd_]
puts $f "$now\t$cwnd\"
$ns at [expr $now+$time] "plotWindow $tcpSource $f"
}

"""
footer = """
$ns at 300 "finish"
puts "Simulation encours!! Veuillez patienter..."
$ns run
"""
#Generation de la topologie
output.write(header)
Simulation(topo,output)

# Fonction principale du projet, elle permet d'analyser les flux présents dans traff.traf
# puis de créer 80% de flux UDP[Pareto], et 20% de flux TCP[Zipf]
GenerationTraffic(traff,output)
output.write(footer)

# Fermeture des fichiers
topo.close()
output.close()
traff.close()
