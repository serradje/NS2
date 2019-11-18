#Create a simulator object
set ns [new Simulator]
$ns color 1 Blue
$ns color 2 Red
# Open the Trace files
set TraceFile [open wired1.tr w]
$ns trace-all $TraceFile
# Open the NAM trace file
set NamFile [open wired1.nam w]
$ns namtrace-all $NamFile
#Open the output files
set f1 [open wiredout1.tr w]
set f2 [open wiredout2.tr w]
#Create 5 nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
#Connect the nodes
$ns duplex-link $n0 $n2 2Mb 10ms DropTail
$ns duplex-link $n1 $n2 2Mb 10ms DropTail
$ns duplex-link $n2 $n3 0.25Mb 100ms DropTail 
# bottleneck link
$ns duplex-link $n3 $n4 2Mb 10ms DropTail
$ns duplex-link $n3 $n5 2Mb 10ms DropTail
#Define que limits
$ns queue-limit $n2 $n3 30
$ns queue-limit $n3 $n2 30
#Define orientation of nodes
$ns duplex-link-op $n0 $n2 orient right-down
$ns duplex-link-op $n1 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n5 orient right-down
#Define a 'finish' procedure
proc finish {} {
global f1 f2
#Close the output files
close $f1
close $f2
#Call xgraph to display the results
#exec xgraph wiredout1.tr wiredout2.tr -geometry 800x400 &
global ns TraceFile NamFile
close $TraceFile
close $NamFile
exec nam wired1.nam &
exit 0
}
#Define a procedure which periodically records the bandwidth received by the
#two traffic sinks sink1/2 and writes it to the three files f1/2.
proc record {} {
global sink1 sink2 f1 f2
#Get an instance of the simulator
set ns [Simulator instance]
#Set the time after which the procedure should be called again
set time 0.5
#How many bytes have been received by the traffic sinks?
set bw1 [$sink1 set bytes_]
set bw2 [$sink2 set bytes_]
#Get the current time
set now [$ns now]
#Calculate the bandwidth (in MBit/s) and write it to the files
puts $f1 "$now [expr $bw1/$time*8/1000000]"
puts $f2 "$now [expr $bw2/$time*8/1000000]"
#Reset the bytes_ values on the traffic sinks
$sink1 set bytes_ 0
$sink2 set bytes_ 0
#Re-schedule the procedure
$ns at [expr $now+$time] "record"
}
#Create three traffic sinks and attach them to the node n3
#TCP N1 and N5
set tcp1 [new Agent/TCP/Newreno]
$ns attach-agent $n0 $tcp1
set sink1 [new Agent/TCPSink/DelAck]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1
$tcp1 set window_ 8000
$tcp1 set packetSize_ 600
#TCP N1 and N5
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP
#TCP N2 and N6
set tcp2 [new Agent/TCP/Newreno]
$ns attach-agent $n1 $tcp2
set sink2 [new Agent/TCPSink/DelAck]
$ns attach-agent $n5 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2
$tcp2 set window_ 8000
$tcp2 set packetSize_ 600
#FTP TCP N2 and N6
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP
#Start logging the received bandwidth
$ns at 0.0 "record"
#Start the traffic sources
$ns at 0.1 "$ftp1 start"
$ns at 10.0 "$ftp2 start"
$ns at 50.0 "$ftp1 stop"
$ns at 45.0 "$ftp2 stop"
#Finish logging the received bandwidth
$ns at 60.0 "finish"
#Run the simulation
$ns run
