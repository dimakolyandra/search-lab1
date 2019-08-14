import logging
import yaml
import unittest
import os
import hashlib

from functools import wraps
from datetime import datetime
from importlib import import_module


REVERSE_SIZE_OF_RECORD = 40
RIGHT_SIZE_OF_RECORD = 10


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


def timer_debug(func: callable, *args, **kwargs):
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


def _get_hash(termin: str) -> str:
    return hashlib.md5(termin.encode('utf-8')).hexdigest()


def get_page_ids_for_termin(termin: str, with_tf_df: bool = False) -> set:
    with open(os.environ['inverse'], 'rb') as reverse_index, \
            open(os.environ['dict'], 'rb') as dictionary:

        while True:
            data = reverse_index.read(REVERSE_SIZE_OF_RECORD)

            if not data:
                break

            if data[:32].decode() == _get_hash(termin):
                result_pages = set()
                offset = int.from_bytes(data[32:36], byteorder='big')
                count = int.from_bytes(data[36:40], byteorder='big')
                dictionary.seek(offset)
                docks = dictionary.read(count * 8)

                start = 0
                for i in range(count):
                    dock_id = int.from_bytes(
                        docks[start:start + 2], byteorder='big')
                    tf = int.from_bytes(
                        docks[start + 2: start + 4], byteorder='big')
                    df = int.from_bytes(
                        docks[start + 4: start + 6], byteorder='big')
                    int.from_bytes(
                        docks[start + 6: start + 8], byteorder='big')
                    start += 8
                    if with_tf_df:
                        result_pages.add((dock_id, tf, df))
                    else:
                        result_pages.add(dock_id)
                return result_pages


def get_page_by_id(dock_id: int) -> dict:
    with open(os.environ["right"], 'rb') as right_index:
        while True:
            try:
                data = right_index.read(RIGHT_SIZE_OF_RECORD)
                if not data:
                    break
                if int.from_bytes(data[:2], byteorder='big') == dock_id:
                    off = int.from_bytes(data[2:6], byteorder='big')
                    title_size = int.from_bytes(data[6:8], byteorder='big')
                    url_size = int.from_bytes(data[8:10], byteorder='big')
                    right_index.seek(off)
                    return {
                        "title": right_index.read(title_size).decode('utf-8'),
                        "url": right_index.read(url_size).decode('utf-8'),
                        "id": dock_id
                    }
            except Exception:
                return {
                    "title": "ERROR",
                    "url": "ERROR",
                    "id": dock_id
                }


def init_environ(cur_file: str):
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(cur_file)), "data")
    os.environ['inverse'] = os.path.join(data_dir, "inverse.out")
    os.environ['right'] = os.path.join(data_dir, "right.out")
    os.environ['dict'] = os.path.join(data_dir, "dict.out")


def init_logging(loglvl: str):
    logging_lvl = loglvl or "info"
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler("indexing.log")
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=getattr(logging, logging_lvl.upper()),
        handlers=[console_handler, file_handler])
