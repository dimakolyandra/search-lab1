import os
import pickle
import logging

from builder_utils import stage_logging


LOGGING_INTERVAL = 100


def read_docs(consts):
    result = dict()
    in_path = os.path.join(consts["data_dir"], "tokenisation.out")
    logging.debug(f"Input file path {in_path}")
    with open(in_path, 'rb') as in_:
        pages = pickle.load(in_)
    for title, page in pages.copy().items():
        result[page["id"]] = {
            "title": title,
            "url": page["url"]
        }
        del pages[title]
    logging.debug(f"Preprocessed pages count: {len(result)}")
    return result


def make_right_index(consts):
    document_index = read_docs(consts)
    out_path = os.path.join(consts["data_dir"], "right.out")

    with open(out_path, 'wb') as f:
        sorted_keys = sorted(document_index.keys())
        offset = len(sorted_keys) * consts["size_of_record_right"]
        page_counter = 0
        for key in sorted_keys:
            if page_counter % LOGGING_INTERVAL:
                logging.debug(
                    f"Saving document {page_counter} from {len(sorted_keys)}")
            title_len = len(document_index[key]['title'].encode('utf-8'))
            url_len = len(document_index[key]['url'].encode('utf-8'))

            f.write(key.to_bytes(2, byteorder='big'))
            f.write(offset.to_bytes(4, byteorder='big'))
            f.write(title_len.to_bytes(2, byteorder='big'))
            f.write(url_len.to_bytes(2, byteorder='big'))
            offset += title_len + url_len

        for key in sorted_keys:
            f.write(document_index[key]['title'].encode('utf-8'))
            f.write(document_index[key]['url'].encode('utf-8'))


@stage_logging
def run(consts: dict, stage_id: int):
    make_right_index(consts)
