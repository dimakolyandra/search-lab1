import os
import pickle
import hashlib
import logging
import sys

from builder_utils import stage_logging, timer_debug, init_stage
from stemmer import Stemmer

LOGGING_INTERVAL = 10000


def save_tokens(token, docs, index_file, dict_file, offset, tf, df):
    token_hash = hashlib.md5(token.encode()).hexdigest()
    index_file.write(token_hash.encode())
    index_file.write(offset.to_bytes(4, byteorder='big'))
    index_file.write(len(docs).to_bytes(4, byteorder='big'))
    for doc in docs:
        dict_file.write(
            int(doc[0]).to_bytes(2, byteorder='big'))
        dict_file.write(
            int(tf[doc[0]]).to_bytes(2, byteorder='big'))
        dict_file.write(
            int(df).to_bytes(2, byteorder='big'))
        dict_file.write(
            int(doc[1]).to_bytes(2, byteorder='big'))


def make_inverse_index(in_path, index_path, dict_path):
    tokens = []
    stemmer = Stemmer()
    with open(in_path, 'rb') as in_:
        tokenisation = pickle.load(in_)
        logging.debug("Pickle data was load")
        count_page_processed = 1
        token_items = tokenisation.items()
        for _, value in token_items:
            for token in value["tokens"]:
                if count_page_processed % LOGGING_INTERVAL == 0:
                    logging.debug(
                        f"Processed {count_page_processed}"
                        f"from {len(token_items)}:")
                    count_page_processed += 1
                tokens.append((stemmer.stem(
                    sys.intern(token[0].lower())),
                    (value["id"], token[1])))
            count_page_processed += 1
    logging.debug(f"Got {len(tokens)} tokens from input, start sorting")
    logging.debug("Start sorting pair token-dockId")
    tokens.sort(key=lambda x: (x[0], x[1][0]))
    logging.debug("Finish sorting pair token-dockId")

    prev_token = None
    docs = list()
    tf = dict()
    offset = i = df = 0
    with open(index_path, "wb") as index_file, \
            open(dict_path, "wb") as dict_file:
        for tuple_ind, token_tuple in enumerate(tokens):
            token = token_tuple[0]
            dock_id = token_tuple[1]
            if i % LOGGING_INTERVAL == 0:
                logging.debug(f"Processed {i} tokens from {len(tokens)}")
            i += 1

            if dock_id[0] in tf:
                tf[dock_id[0]] += 1
            else:
                tf[dock_id[0]] = 1

            if prev_token is None or token.lower() == prev_token.lower():
                prev_token = token
                docs.append(dock_id)
                continue
            else:
                tf[dock_id[0]] -= 1
                df = len(set([dock_id for dock_id, _ in docs]))
                save_tokens(
                    prev_token, docs,
                    index_file, dict_file,
                    offset, tf, df)
                offset += 8 * len(docs)
                if tuple_ind != len(tokens) - 1:
                    docs = [dock_id]
                    tf = {dock_id[0]: 1}
                prev_token = token
        save_tokens(prev_token, docs, index_file, dict_file, offset, tf, df)


@stage_logging
def run(consts: dict, stage_id: int):
    in_path, _ = init_stage(consts, stage_id, with_logging=False)
    inverse_index_path = os.path.join(consts["data_dir"], "inverse.out")
    dict_index_path = os.path.join(consts["data_dir"], "dict.out")

    logging.debug(f"Inverse index file: {inverse_index_path}")
    logging.debug(f"Inverse index file: {dict_index_path}")

    timer_debug(
        make_inverse_index, in_path, inverse_index_path, dict_index_path)
