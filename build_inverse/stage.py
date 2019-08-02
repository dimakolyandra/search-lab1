import os
import pickle
import hashlib
import logging

from builder_utils import stage_logging, timer_debug, init_stage


LOGGING_INTERVAL = 100000


def save_tokens(token, docs, index_file, dict_file, offset):
    token_hash = hashlib.md5(token.encode()).hexdigest()
    index_file.write(token_hash.encode())
    index_file.write(offset.to_bytes(4, byteorder='big'))
    index_file.write(len(docs).to_bytes(4, byteorder='big'))
    for doc in docs:
        dict_file.write(
            int(doc[0]).to_bytes(2, byteorder='big'))
        dict_file.write(
            int(doc[1]).to_bytes(2, byteorder='big'))


def make_inverse_index(in_path, index_path, dict_path):
    tokens = []
    with open(in_path, 'rb') as in_:
        tokenisation = pickle.load(in_)
        # keys = set(list(tokenisation.keys())[:1000])
        # tokenisation = {k: v for k, v in tokenisation.items() if k in keys}
        for _, value in tokenisation.items():
            for token in value["tokens"]:
                tokens.append(
                    (token[0].decode("utf-8").lower(),
                        (value["id"], token[1])))
    logging.debug(f"Got {len(tokens)} tokens from input, start sorting")
    logging.debug("Start sorting pair token-dockId")
    tokens.sort(key=lambda x: (x[0], x[1][0]))
    logging.debug("Finish sorting pair token-dockId")

    prev_token = None
    docs = list()
    offset = i = 0
    with open(index_path, "wb") as index_file, \
            open(dict_path, "wb") as dict_file:
        for tuple_ind, token_tuple in enumerate(tokens):
            token = token_tuple[0]
            dock_id = token_tuple[1]
            if i % LOGGING_INTERVAL == 0:
                logging.debug(f"Processed {i} tokens from {len(tokens)}")
            i += 1
            if prev_token is None or token.lower() == prev_token.lower():
                prev_token = token
                docs.append(dock_id)
                continue
            else:
                save_tokens(prev_token, docs, index_file, dict_file, offset)
                offset += 4 * len(docs)
                if tuple_ind != len(tokens) - 1:
                    docs = [dock_id]
                prev_token = token
        save_tokens(prev_token, docs, index_file, dict_file, offset)


@stage_logging
def run(consts: dict, stage_id: int):
    in_path, _ = init_stage(consts, stage_id, with_logging=False)
    inverse_index_path = os.path.join(consts["data_dir"], "inverse.out")
    dict_index_path = os.path.join(consts["data_dir"], "dict.out")

    logging.debug(f"Inverse index file: {inverse_index_path}")
    logging.debug(f"Inverse index file: {dict_index_path}")

    timer_debug(
        make_inverse_index, in_path, inverse_index_path, dict_index_path)
