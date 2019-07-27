import logging

from builder_utils import stage_logging, timer_debug


@stage_logging
def run(consts, stage_id):
    logging.info("Building index")
