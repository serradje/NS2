#Create a simulator object
set ns [new Simulator]

#Define different colors for data flows (for NAM)
$ns color 0 Blue
$ns color 1 Red
$ns color 2 Green
$ns color 3 Cyan

#Open the NAM trace file
set nf [open out.nam w]
$ns namtrace-all $nf
#~ set f0 [open trace.tr w]
#~ $ns trace-all $f0

set qsize [open queuesize.tr w]
set qbw [open queuebw.tr w]
set qlost [open queuelost.tr w]

#Define a 'finish' procedure
proc finish {} {
        global ns nf qsize qbw qlost 
        $ns flush-trace
        #Close the NAM trace file
        close $nf
        close $qsize
		close $qbw
		close $qlost
        #Execute NAM on the trace file
        exec nam -a out.nam &
        exit 0
}

set old_departure 0
proc record {} {
		global ns qmon_size qmon_bw qmon_lost qsize qbw qlost old_departure
		set ns [Simulator instance]
		set time 0.05
		set now [$ns now]

		$qmon_size instvar size_ pkts_ barrivals_ bdepartures_ parrivals_ pdepartures_ bdrops_ pdrops_ 
		puts $qsize "$now [$qmon_size set size_]"

		puts $qbw "$now [expr ($bdepartures_ - $old_departure)/$time*8/1000000]" 
		set old_departure $bdepartures_

		puts $qlost "$now $pdrops_  $bdrops_"
		$ns at [expr $now+$time] "record"
}

# Create 4 nodes
for { set i 0 } { $i < 4 } { incr i } {
		set n($i) [$ns node]
}

# Create links between the 4 nodes and create 25 nodes and links between the 4 nodes and 25 nodes
for { set i 0 } { $i < 4 } { incr i } {
	#noeud(0->1) à 1,5 afin d'etre surchargé
	#~ if {$i == 0}
	#~ {
	#~ $ns simplex-link $n($i) $n([expr { ($i+1) % 4 }]) 1.5Mb 10ms DropTail
	#~ }
	
   $ns simplex-link $n($i) $n([expr ($i+1) % 4 ]) 2Mb 10ms DropTail
   #$ns queue-limit $n($i) $n([expr { ($i+1) % 4 }]) 20
   
  for {set j 0} { $j < 25 } { incr j } {
	set n($i.$j) [$ns node]
	$ns duplex-link $n($i.$j) $n($i) 1Mb 10ms DropTail ;
  }
}

#~ #Give node position (for NAM)
$ns simplex-link-op $n(0) $n(1) orient right
$ns simplex-link-op $n(1) $n(2) orient down
$ns simplex-link-op $n(2) $n(3) orient left
$ns simplex-link-op $n(3) $n(0) orient up

# Create  agent attach
for { set i 0 } { $i < 4 } { incr i } {
  for { set j 0 } { $j < 25 } { incr j } {
	  
      set udp($i.$j) [new Agent/UDP]
      $ns attach-agent $n($i.$j) $udp($i.$j)
	  $udp($i.$j) set fid_ $i
	  
      set null($i.$j) [new Agent/Null]
      $ns attach-agent $n($i.$j) $null($i.$j)
      
      set cbr($i.$j) [new Application/Traffic/CBR]
      $cbr($i.$j) attach-agent $udp($i.$j)
      
      $cbr($i.$j) set packetSize_ 1460
	  $cbr($i.$j) set rate_ 1Mb   
      
	}
}

#Setup a UDP connection
for { set i 0 } { $i < 4 } { incr i } {
  for { set j 0 } { $j < 25 } { incr j } {
	  #set k [expr { ($i+1) % 4 }]
      $ns connect $udp($i.$j) $null([expr ($i+1) % 4 ].$j)
  }
}

#Schedule events for the CBR agents
for { set i 0 } { $i < 4 } { incr i } {
  for { set j 0 } { $j < 25 } { incr j } {
      $ns at 0.5 "$cbr($i.$j) start"
      $ns at 4.5 "$cbr($i.$j) stop"
    }
}

#~ #Monitor the queue for link (n2-n3). (for NAM)
#~ $ns duplex-link-op $n(0) $n(1) queuePos 0.5
#~ $ns duplex-link-op $n(0) $n(2) queuePos 0.5
#~ $ns duplex-link-op $n(1) $n(2) queuePos 0.5
#set angle [ expr $angle -x *(0.5/25) ]
#if($i == 0)
#set angle 1.0


#Rempli le fichier utile pour avoir accès aux files d'attentes
#~ set drop [$ns monitor-queue $n(0) $n(1)  [open queue.tr w] 0.1]
  #~ [$ns link $n(0) $n(1)] queue-sample-timeout;

set qf_size [open queue.size w]
set qmon_size [$ns monitor-queue $n(0) $n(1) $qf_size 0.05]

#Call the finish procedure after 5 seconds of simulation time
$ns at 0.0 "record"
$ns at 5.0 "finish"

#Run the simulation
$ns run

