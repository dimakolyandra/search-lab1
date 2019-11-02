import json
import pickle
import logging
import re
import urllib.parse
import sys

from builder_utils import stage_logging, timer_debug, init_stage


WIKI_URL_TEMPL = "https://ru.wikipedia.org/wiki/{}"


def tokenise(data: dict) -> dict:
    tokens_data = dict()
    regex_token = re.compile(r'\w+')
    token_count = 0
    for page in data:
        title = page["title"]
        tokens = [(sys.intern(t[1].group(0)), t[0])
                  for t in enumerate(
                      re.finditer(regex_token, page["text"]), 1)]
        tokens_data[title] = {
            "url": WIKI_URL_TEMPL.format(urllib.parse.quote(title)),
            "tokens": tokens,
            "id": page["id"]
        }
        token_count += len(tokens)
    logging.debug("Total size of tokens: %d", token_count)
    return tokens_data


@stage_logging
def run(consts: dict, stage_id: int):

    in_path, out_path = init_stage(consts, stage_id)

    with open(in_path, encoding="utf-8") as data_in,\
            open(out_path, "wb") as data_out:
        data = timer_debug(json.load, data_in)
        logging.debug(f"Loaded json with {len(data)} pages")
        tokens_data = timer_debug(tokenise, data)
        logging.debug("Finish tokenizing pages")
        timer_debug(pickle.dump, tokens_data, data_out)
        logging.debug("Finish dumping pages")
