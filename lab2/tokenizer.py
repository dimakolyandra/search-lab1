import re
import os
import pickle
import time
from datetime import datetime as time


START_PAGE_TITLE = "++++++++++START_PAGE_TITLE++++++++++"
START_PAGE_TEXT = "++++++++++START_PAGE_TEXT++++++++++"
END_PAGE_TEXT = "++++++++++END_PAGE_TEXT++++++++++"


regex_tokens = re.compile(r'\w+')


def get_text_token(text):
    tokens = re.finditer(regex_tokens, text)
    return [(elem[1].group(0), elem[0]) for elem in enumerate(tokens, 1)]


def page_iterator(data):
    is_text = False
    title = None
    data = data.split('\n')
    text = []
    for i in range(len(data)):

        if data[i - 1] == START_PAGE_TITLE:
            title = data[i]

        elif data[i] == START_PAGE_TEXT:
            is_text = True
            continue

        elif data[i] == END_PAGE_TEXT:
            yield title, '\n'.join(text)
            is_text = False
            text = []
            title = None
        
        if is_text:
            text.append(data[i])


def read_bufferized():
    list_files = os.listdir('./tokens_pages')
    for file in list_files:
        with open(f'./tokens_pages/{file}') as file:
            data = file.read()
            yield from page_iterator(data)


def save_tokens():
    tokens = dict()
    i = 0
    for title, text in read_bufferized():
        i += 1
        tokens[title] = {
            "url": f"https://ru.wikipedia.org/wiki/{title}",
            "tokens": get_text_token(text),
            "id": i
        }
        if i % 5000 == 0 or i == 49995:
            pickle.dump(tokens, open(f"./tokens_data/tokens-{i}.pickle", "wb"))
            tokens = dict()


def main():
    t1 = time.now()
    save_tokens()
    print("Time: " + str(time.now() - t1))


if __name__ == "__main__":
    main()
