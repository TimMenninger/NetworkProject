# CS143Project (Configurable Network Simulator, CS 143, Caltech, Fall 2015)
## Ricky Galliani, Tim Menninger, Rush Joshi, and Schaeffer Reed

## Repository organization: 

- All Python code for our simulator (modules and classes) are in the
*.py files of the src directory of this repository.

- All network configuration files (including a template file that can be 
used to create new network configuration files) are in in/test_configs/*

- Run-time logs are written out to in out/log/*

- Data files are written out to in out/data/*

- The misc/clean_up.sh script can be used to clean up the repository

## Running the simulation:

$ python3 src/simulate.py ../in/test_configs/<network_config_file>

[or]

$ python3 in/simulate.py in/test_configs/<network_config_file>

Test Case 0
$ python3 src/simulate.py in/test_configs/case_0.txt

Test Case 1
$ python3 src/simulate.py in/test_configs/case_0.txt

Test Case 2
$ python3 src/simulate.py in/test_configs/case_0.txt

Note: the 'Simulation Progress' update presented to standard output while
the simualation is running does not accurately reflect the simulation 
progress when Test Case 3 (and probably all multi-flow networks) is running.
