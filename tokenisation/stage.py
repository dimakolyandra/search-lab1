import json
import pickle
import logging
import os
import re
import urllib.parse

from builder_utils import stage_logging, timer_debug


WIKI_URL_TEMPL = "https://ru.wikipedia.org/wiki/{}"


def tokenise(data):
    tokens_data = dict()
    regex_token = re.compile(r'\w+')
    for page in data:
        title = page["title"]
        tokens_data[title] = {
            "url": WIKI_URL_TEMPL.format(urllib.parse.quote(title)),
            "tokens": [(t[1].group(0), t[0])
                       for t in enumerate(
                       re.finditer(regex_token, page["text"]), 1)],
            "id": page["id"]
        }
    return tokens_data


@stage_logging
def run(consts, stage_id):
    stage_name = consts["stages"][stage_id]
    stage_prev = consts["stages"][stage_id - 1]
    logging.debug(f"Previous stage is {stage_prev}")

    in_path = os.path.join(consts["data_dir"], f"{stage_prev}.out")
    out_path = os.path.join(consts["data_dir"], f"{stage_name}.out")
    logging.debug(f"Input file path {in_path}")
    logging.debug(f"Output file path {out_path}")

    with open(in_path, encoding="utf-8") as data_in,\
            open(out_path, "wb") as data_out:
        data = timer_debug(json.load, data_in)
        logging.debug(f"Loaded json with {len(data)} pages")
        tokens_data = timer_debug(tokenise, data)
        logging.debug("Finish tokenizing pages")
        timer_debug(pickle.dump, tokens_data, data_out)
        logging.debug("Finish dumping pages")
