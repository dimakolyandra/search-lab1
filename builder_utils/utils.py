import logging
import yaml
import unittest
import os

from functools import wraps
from datetime import datetime
from importlib import import_module


def load_yml(file: str) -> dict:
    with open(file) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(f"Unable to load yml file: {file}", exc)


def stage_logging(func):
    @wraps(func)
    def wrapper(*args):
        stage = args[0]["stages"][args[1]]
        logging.info(f"{'-' * 10} Start {stage} stage of indexing {'-' * 10}")
        t1 = datetime.now()
        func(*args)
        t2 = datetime.now()
        logging.info(f"Stage total time: {t2 - t1}")
        logging.info(f"{'-' * 10} Finish {stage} stage of indexing {'-' * 10}")
    return wrapper


def timer_debug(func, *args, **kwargs):
    t1 = datetime.now()
    res = func(*args, **kwargs)
    t2 = datetime.now()
    logging.debug(f"Function {func.__name__} takes: {t2 - t1} time")
    return res


def run_test_for_stage(stage_name: str) -> bool:
    try:
        test_module = import_module(f"{stage_name}.test")
    except ModuleNotFoundError:
        logging.debug(f"There is no tests for stage: {stage_name}")
        return True
    else:
        suite = unittest.TestLoader().loadTestsFromModule(test_module)
        test_results = unittest.TextTestRunner(verbosity=1).run(suite)
        if test_results.failures:
            return False
        if test_results.errors:
            return False
        return True


def init_stage(consts: dict, stage_id: int, with_logging: bool = True):
    stage_name = consts["stages"][stage_id]

    if stage_id == 0:
        in_path = os.path.join(consts["data_dir"], consts["input_file_name"])
        out_path = os.path.join(consts["data_dir"], f"{stage_name}.out")
    else:
        stage_prev = consts["stages"][stage_id - 1]
        logging.debug(f"Previous stage is {stage_prev}")

        in_path = os.path.join(consts["data_dir"], f"{stage_prev}.out")
        out_path = os.path.join(consts["data_dir"], f"{stage_name}.out")

    if with_logging:
        logging.debug(f"Input file path {in_path}")
        logging.debug(f"Output file path {out_path}")

    return in_path, out_path
