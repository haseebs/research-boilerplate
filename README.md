# Research Boilerplate
Boilerplate code for mysql database logger, configs and experiment management.

## How to run
1. Install requirements:
``` bash
pip install -r requirments.txt
``` 

2. Add the correct db credentials to configs/db/credentials.yaml. You can get a database server on Compute Canada by following these instructions: 
https://docs.computecanada.ca/wiki/Database_servers 

3. Set db_prefix to your compute canada username in configs/config.yaml (This is required because CC only allows you to make databases that start with your CC username). 

4. Run the following command to log some data to the database: 

For a single run:
```bash
python main.py +args.run=123 ++hydra.mode=RUN
```

For a sweep of multiple runs:
```bash
python main.py +args.run=300
```

For an optuna sweep:
```bash
TODO
```

For directly running slurm sweeps on CC:
```bash
TODO
```

The command will run 5 jobs and and store the data in the database. You can look at the data by executing the following sql queries: 

1. use COMPUTE_CANADA_USERNAME_new_experiment123; 
2. select * from runs; 
3. select * from errors;
4. select * from summary_table; 
