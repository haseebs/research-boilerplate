import random
import hydra
import torch
import numpy as np

from datetime import timedelta
from timeit import default_timer as timer
from omegaconf import DictConfig, OmegaConf
from hydra.core.hydra_config import HydraConfig

from utils import utils
from experiment import ExperimentManager, Metric


@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig) -> None:
    start = timer()
    args = cfg.args
    if HydraConfig.get().mode.value == 2:  # check whether its a sweep
        args.run += HydraConfig.get().job.num
    print(OmegaConf.to_yaml(cfg))
    exp = ExperimentManager(cfg.db_name, args, cfg.db_prefix, cfg.db)
    tables = {}
    for table_name in list(cfg.schema.keys()):
        columns = cfg.schema[table_name].columns
        primary_keys = cfg.schema[table_name].primary_keys
        tables[table_name] = Metric(table_name, columns, primary_keys, exp)

    utils.set_seed(args.seed)

    for step in range(0, 100):
        tables["errors"].add_data([args.run, step, random.random()])
        if not step % 10:
            tables["errors"].commit_to_database()

    total_time = timedelta(seconds=timer() - start).seconds / 60
    tables["summary"].add_data(
        [
            args.run,
            step,
            random.random(),
            total_time
        ]
    )
    tables["summary"].commit_to_database()
    tables["errors"].commit_to_database()
    print( "Total time taken: ", total_time, " minutes")


if __name__ == "__main__":
    main()
