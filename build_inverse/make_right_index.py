import os
import pickle
from urllib.parse import quote


INPUT_DATA_DIR = './tokens_data'
OUTPUT_DATA_DIR = './tokens_prepared'
OUTPUT_INDEX_DIR = './index'
SIZE_OF_RECORD = 10


def read_docs(file_names):
    index = {}
    for file in file_names:
        tokens = pickle.load(open(os.path.join(INPUT_DATA_DIR, file), 'rb'))
        i = 0
        for key, val in tokens.items():
            i += 1
            index[val['id']] = {
                'url': quote(val['url'], safe="https://ru.wikipedia.org/wiki/"),
                'title': key
            }
    return index


def make_right_index(file_names):
    document_index = read_docs(file_names)

    with open(os.path.join(OUTPUT_INDEX_DIR, "right_index.txt"), 'wb') as f:
        sorted_keys = sorted(document_index.keys())
        offset = len(sorted_keys) * SIZE_OF_RECORD
        for key in sorted_keys:
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


def main():
    files = os.listdir(INPUT_DATA_DIR)
    # make_right_index(files)

    with open(os.path.join(OUTPUT_INDEX_DIR, "right_index.txt"), 'rb') as f:
        
        for _ in range(50000):
            data = f.read(SIZE_OF_RECORD)

            if int.from_bytes(data[:2], byteorder='big') == 10917:
                off = int.from_bytes(data[2:6], byteorder='big')
                title_size = int.from_bytes(data[6:8], byteorder='big')
                url_size = int.from_bytes(data[8:10], byteorder='big')
                f.seek(off)
                title = f.read(title_size).decode('utf-8')
                url = f.read(url_size).decode('utf-8')
                print(title)
                print(url)


if __name__ == "__main__":
    main()
