# CS143Project
## Ricky Galliani, Tim Menninger, Rush Joshi, and Schaeffer Reed
### Configurable Network Simulator 
#### CS 143 (Caltech, Fall 2015)

### Notes about repository organization: 

- All Python code for our simulator (modules and classes) are in the
*.py files of the src directory of this repository.

- All network configuration files (including a template file that can be 
used to create new network configuration files) are in in/test_configs/*

- Run-time logs are written out to in out/log/*

- Data files are written out to in out/data/*

- The misc/clean_up.sh script can be used to clean up the repository

### Running the simulation:

$ python3 simulate.py ../in/test_configs/<network_config_file>

[or]

$ python3 in/simulate.py in/test_configs/<network_config_file>

Test Case 0
$ python3 simulate.py ../in/test_configs/case_0.txt

Test Case 1
$ python3 simulate.py ../in/test_configs/case_1.txt

Test Case 2
$ python3 simulate.py misc/test_configs/case_2.txt

