# CS143Project (Configurable Network Simulator, CS 143, Caltech, Fall 2015)
## Ricky Galliani, Tim Menninger, Rush Joshi, and Schaeffer Reed

## Repository organization: 

- All Python code for our simulator (modules and classes) are in the
*.py files of the home directory of this repository.

- All network configuration files (including a template file that can be 
used to create new network configuration files) are in misc/test_configs/*

- Run-time logs are written out to in misc/log/*

- Data files are written out to in misc/data/*

- The misc/clean_up.sh script can be used to clean up the repository

## Running the simulation:

$ python simulate.py <network_config_file>

Test Case 0
$ python simulate.py misc/test_configs/case_0.txt

Test Case 1
$ python simulate.py misc/test_configs/case_1.txt

Test Case 2
$ python simulate.py misc/test_configs/case_2.txt

