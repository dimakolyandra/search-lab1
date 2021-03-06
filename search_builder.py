import os
import logging
from importlib import import_module
from argparse import ArgumentParser
from builder_utils import run_test_for_stage, init_logging


STAGE_INDEXING = ["preprocessing", "tokenisation",
                  "build_inverse", "build_right"]

INDEXING_CONSTANTS = {
    "data_dir": os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data"),
    "stages": STAGE_INDEXING,
    "input_file_name": "data.in",
    "config_file_name": "config.yml",
    "size_of_record": 40,
    "size_of_record_right": 10
}


def _init_argparser() -> ArgumentParser:
    text = "Script for ruling indexation process." \
           "Data structure in config.yml, input file with name data.in"
    parser = ArgumentParser(description=text)
    parser.add_argument(
        "--stage", "-s",
        help=f"Stage of indexing, one of: {STAGE_INDEXING}",
        required=True)
    parser.add_argument(
        "--allstages", "-a",
        help=f"Process all stages of indexing, or only passed",
        action="store_true")
    parser.add_argument(
        "--withtests", "-w",
        help="Run tests after stage finishing",
        action="store_true")
    parser.add_argument(
        "--onlytests", "-o",
        help="Run tests after stage finishing",
        action="store_true")
    parser.add_argument("--loglvl", "-l", help=f"Logging level")
    return parser


def handle_stage_tests(stage: str):
    if args.withtests:
        test_success = run_test_for_stage(stage)
        if not test_success:
            logging.error(f"Tests failed for stage {stage}")
            exit(2)


if __name__ == "__main__":
    parser = _init_argparser()
    args = parser.parse_args()
    init_logging(args.loglvl)
    try:
        stage_target_id = STAGE_INDEXING.index(args.stage)
    except ValueError:
        logging.error(
            "Unknown stage of indexing: %s expected one of %s" %
            (args.stage, ', '.join(STAGE_INDEXING)), exc_info=True)
        exit(1)
    if args.allstages:
        stage_gen = enumerate(
            STAGE_INDEXING[:stage_target_id + 1])
        for stage_id, stage in stage_gen:
            if not args.onlytests:
                module = import_module(stage)
                module.run(INDEXING_CONSTANTS, stage_id)
            handle_stage_tests(stage)
    else:
        if not args.onlytests:
            module = import_module(args.stage)
            module.run(INDEXING_CONSTANTS, stage_target_id)
        handle_stage_tests(args.stage)
