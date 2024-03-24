import random
import hydra
import torch
import numpy as np
import logging

from datetime import timedelta
from rich.pretty import pretty_repr
from timeit import default_timer as timer
from omegaconf import DictConfig, OmegaConf
from hydra.core.hydra_config import HydraConfig

from utils import utils
from utils.utils import prep_cfg_for_db
from experiment import ExperimentManager, Metric

log = logging.getLogger(__name__)

@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig) -> None:
    start = timer()
    if HydraConfig.get().mode.value == 2:  # check whether its a sweep
        cfg.run += HydraConfig.get().job.num
        log.info(f'Running sweep... Run ID: {cfg.run}')
    log.info(f"Output directory  : {hydra.core.hydra_config.HydraConfig.get().runtime.output_dir}")
    flattened_cfg = prep_cfg_for_db(OmegaConf.to_container(cfg), to_remove=["schema", "db"])
    log.info(pretty_repr(flattened_cfg))
    exp = ExperimentManager(cfg.db_name, flattened_cfg, cfg.db_prefix, cfg.db)
    tables = {}
    for table_name in list(cfg.schema.keys()):
        columns = cfg.schema[table_name].columns
        primary_keys = cfg.schema[table_name].primary_keys
        tables[table_name] = Metric(table_name, columns, primary_keys, exp)

    utils.set_seed(cfg.seed)

    for step in range(0, 100):
        tables["errors"].add_data([cfg.run, step, random.random()])
        if not step % 10:
            tables["errors"].commit_to_database()

    total_time = timedelta(seconds=timer() - start).seconds / 60
    tables["summary"].add_data(
        [
            cfg.run,
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

