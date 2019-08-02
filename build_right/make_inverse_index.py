import os
import hashlib


DATA_DIR = './tokens_prepared'
OUTPUT_INDEX_DIR = './index'
SIZE_OF_RECORD = 40


def save_tokens(token, docs, index_file, dict_file, offset):
    docs = sorted(docs, key=lambda x: int(x.split(':')[0]))

    token_hash = hashlib.md5(token.encode('utf-8')).hexdigest()
    index_file.write(token_hash.encode())

    index_file.write(offset.to_bytes(4, byteorder='big'))
    index_file.write(len(docs).to_bytes(4, byteorder='big'))
    for doc in docs:
        dict_file.write(int(doc.split(':')[0]).to_bytes(2, byteorder='big'))
        dict_file.write(int(doc.split(':')[1]).to_bytes(2, byteorder='big'))


def main():
    i = 0
    with open(os.path.join(DATA_DIR, 'sorted_2.txt')) as file, \
         open(os.path.join(OUTPUT_INDEX_DIR, 'reverse_index.txt'), 'wb') as result_index, \
         open(os.path.join(OUTPUT_INDEX_DIR, 'dictionary.txt'), 'wb') as dict_index:
        prev_line = None
        docs = list()
        offset = 0

        for line in file:
            if i % 100000 == 0:
                print(i)

            i += 1

            docs.append(line.split('\t')[1].strip())
                            
            if prev_line is None or line.lower().split('\t')[0] == prev_line.lower().split('\t')[0]:
                prev_line = line
                continue

            else:

                save_tokens(prev_line.split('\t')[0], docs, result_index, dict_index, offset)
                offset += 4 * len(docs)
                docs = list()

            prev_line = line
            

def test(token):
    token_hash = hashlib.md5(token.encode('utf-8')).hexdigest()

    with open(os.path.join(OUTPUT_INDEX_DIR, 'reverse_index.txt'), 'rb') as result_index, \
         open(os.path.join(OUTPUT_INDEX_DIR, 'dictionary.txt'), 'rb') as dict_index:

        while True:

            data = result_index.read(SIZE_OF_RECORD)

            if data is None:
                break

            j = 0

            if data[:32].decode() == token_hash:
                offset = int.from_bytes(data[32:36], byteorder='big')
                count  = int.from_bytes(data[36:40], byteorder='big')
                print("COUNT: " + str(count))
                dict_index.seek(offset)
                docks = dict_index.read(count * 4)
                start = 0
                for i in range(count):
                    dock_id = int.from_bytes(docks[start:start+2], byteorder='big')
                    pos = int.from_bytes(docks[start + 2: start + 4], byteorder='big')
                    start += 4
                    print(dock_id)
                return


if __name__ == "__main__":
    # main()
    test('путин')