import os
import hashlib


REVERSE_SIZE_OF_RECORD = 40
RIGHT_SIZE_OF_RECORD = 10


def _get_hash(termin):
    return hashlib.md5(termin.encode('utf-8')).hexdigest()


def get_page_ids_for_termin(termin):
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
                docks = dictionary.read(count * 4)

                start = 0
                for i in range(count):
                    dock_id = int.from_bytes(
                        docks[start:start + 2], byteorder='big')
                    int.from_bytes(
                        docks[start + 2: start + 4], byteorder='big')
                    start += 4
                    result_pages.add(dock_id)
                return result_pages


def get_page_by_id(dock_id):
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
