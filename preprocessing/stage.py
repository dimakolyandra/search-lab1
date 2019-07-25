import os
import logging
import pprint
import json

from builder_utils import load_yml, stage_logging, timer_debug


def yield_pages(data_in, page_struct):
    page = []
    for line in data_in:
        page.append(line)
        if page_struct["end_subst"] in line:
            yield '\n'.join(page)
            page.clear()


def parse_page_field(page, struct):
    start_subs = struct["start_subst"]
    end_subs = struct["end_subst"]
    start = page.index(start_subs) + len(start_subs)
    end = page.index(end_subs)
    return page[start:end]


def parse_page(page_id, page, page_struct):
    return {
        "id": page_id,
        "title": parse_page_field(page, page_struct["title"]),
        "text": parse_page_field(page, page_struct["text"])
    }


def get_conf(consts):
    conf_file = os.path.join(consts["data_dir"], consts["config_file_name"])
    logging.debug("Loading yml config from: %s", conf_file)
    conf = load_yml(conf_file)["preprocessing"]
    logging.debug("Loaded config:\n " + str(pprint.pformat(conf)))
    return conf


@stage_logging
def run(consts, stage_id):
    stage_name = consts["stages"][stage_id]
    conf = get_conf(consts)

    in_path = os.path.join(consts["data_dir"], consts["input_file_name"])
    out_path = os.path.join(consts["data_dir"], f"{stage_name}.out")
    logging.debug(f"Input file path {in_path}")
    logging.debug(f"Output file path {out_path}")

    with open(in_path, encoding='utf-8') as data_in, \
            open(out_path, "w", encoding='utf-8') as data_out:
        preprocessed_pages = list()
        for page_id, page in enumerate(yield_pages(data_in, conf["page"]), 1):
            preprocessed_pages.append(parse_page(page_id, page, conf["page"]))
        timer_debug(
            json.dump, preprocessed_pages,
            data_out, ensure_ascii=False, indent=4)
