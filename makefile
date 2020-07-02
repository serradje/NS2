PYTHON = python -E
NS2 = ns

simulation:
	$(NS2) simulation.tcl

generation: genSimulation.py topo.top traff.traf
	$(PYTHON) genSimulation.py topo.top traff.traf

analyse: 
	awk -f analyse.awk trace.tr
	
clean:
	rm -f simulation.tcl trace.tr queue/* congestion/*
