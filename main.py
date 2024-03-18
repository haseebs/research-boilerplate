import random
import hydra
import torch
import numpy as np
import logging

from datetime import timedelta
from timeit import default_timer as timer
from omegaconf import DictConfig, OmegaConf
from hydra.core.hydra_config import HydraConfig

from utils import utils
from experiment import ExperimentManager, Metric

log = logging.getLogger(__name__)

@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig) -> None:
    start = timer()
    args = cfg.args
    if HydraConfig.get().mode.value == 2:  # check whether its a sweep
        args.run += HydraConfig.get().job.num
        log.info(f'Running sweep... Run ID: {args.run}')
    log.info(OmegaConf.to_yaml({**args, **args})) # change 2nd args to another nested config
    exp = ExperimentManager(args.db_name, {**args,**cfg.agent}, args.db_prefix, cfg.db)
    tables = {}
    for table_name in list(cfg.schema.keys()):
        columns = cfg.schema[table_name].columns
        primary_keys = cfg.schema[table_name].primary_keys
        tables[table_name] = Metric(table_name, columns, primary_keys, exp)

    utils.set_seed(args.seed)

    for step in range(0, 100):
        tables["errors"].add_data([args.run,
                                   step,
                                   random.random(),
                                   "teest",
                                   [1,2,3,4],
                                   {"param1": 1,
                                    "param2": 3}
                                   ])
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
    log.info(f'Total time taken: {total_time}  minutes')



if __name__ == "__main__":
    main()
