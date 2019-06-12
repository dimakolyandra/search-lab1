import re
import json
import os
from utils import get_page_ids_for_termin, get_page_by_id


TF_DIR = './index/tf_data'
IDF_DIR = './index/idf_data'

idf = json.load(open(os.path.join(IDF_DIR, 'idf.data')))


def find_tf(token, dock_id):
    with open(os.path.join(TF_DIR, str(dock_id))) as f:
        for line in f:
            if line.split(' ')[0] == token:
                return float(line.split(' ')[1])
        return 0


class SearchEngine:

    PAGE_COUNT = 49995

    class SearchResult:

        tokens = []

        def __init__(self, data, is_not=False):
            if type(data) == str:
                self.tokens.append(data)
                dock_ids = get_page_ids_for_termin(data)
                if is_not:
                    dock_ids = set(range(SearchEngine.PAGE_COUNT)) - dock_ids
                self.dock_ids = dock_ids

            elif type(data) == set:
                if is_not:
                    self.dock_ids = set(range(1, SearchEngine.PAGE_COUNT)) - data
                else:
                    self.dock_ids = data

        def __and__(self, another):
            return SearchEngine.SearchResult(self.dock_ids & another.dock_ids)

        def __or__(self, another):
            return SearchEngine.SearchResult(self.dock_ids | another.dock_ids)

        def __iter__(self):
            docks = list()
            if self.dock_ids:
                for dock_id in self.dock_ids:
                    tf_idf = 0
                    for token in self.tokens:
                        tf_idf += find_tf(token, dock_id) * idf.get(token, 0)
                    docks.append((dock_id, tf_idf))
                docks = sorted(docks, key=lambda x: x[1], reverse=True)
                docks = [(get_page_by_id(dock_id[0]), dock_id[1]) for dock_id in docks]
            return iter(docks)

    class SearchRequest:
        
        PRIORITY = {
            "&": 2,
            "|": 2,
            "(": 1,
            ")": 1,
            "#": -1
        }

        @classmethod
        def get_request(cls, request: str) -> list:
            request  = cls._prepare_request(request)
            if not cls.is_valid(request):
                raise ValueError("Not valid request")
            return cls._get_polish_inverse(request)
        
        @classmethod
        def _get_polish_inverse(cls, experssion: str) -> list:
            items = list(experssion)
            stack = ["#"]
            result = list()
            term_buf = ''
            for item in items:
                if item.isalpha():
                    term_buf += item
                elif item == "(":
                    stack.append(item)
                elif item == ")":
                    if term_buf:
                        result.append(term_buf)
                        term_buf = ''
                    while True:
                        stack_head = stack.pop()
                        if stack_head == "(":
                            break
                        result.append(stack_head)
                elif item == "!":
                    stack.append(item)
                elif item in cls.PRIORITY.keys():
                    if term_buf:
                        result.append(term_buf)
                        term_buf = ''
                    while True:
                        stack_head = stack.pop()
                        if cls.PRIORITY[stack_head] < cls.PRIORITY[item]:
                            stack.append(stack_head)
                            break
                        result.append(stack_head)
                    stack.append(item)

            if term_buf:
                result.append(term_buf)

            for i in range(len(stack)):
                result.append(stack[len(stack) - i - 1])

            return result[:-1]

        @staticmethod
        def is_valid(request: str) -> list:
            return True

        @staticmethod
        def _prepare_request(request: str) -> str:
            result_request = []
            prev = ''
            request = (request
                .replace('(', ' ( ')
                .replace(')', ' ) ')
                .replace('&&', ' && ')
                .replace('||', ' || ')
                .replace('!', ' ! '))

            res = list(filter(None, re.findall(r'[^\s]*', request)))
            for i in range(len(res) - 1):
                result_request.append(res[i])
                if (res[i + 1] != "&&" and 
                        (res[i + 1].isalpha() or 
                            res[i + 1] == "(" or 
                            res[i + 1] == "!") and 
                        res[i] != "(" and 
                        res[i] != "||" and 
                        res[i] != "&&" and
                        res[i] != "!"):
                    result_request.append("&&")
            result_request.append(res[-1])
            return ''.join(result_request).replace('||', '|').replace('&&', '&')

    @classmethod
    def search(cls, request: str) -> SearchResult:
        request_stack = cls.SearchRequest.get_request(request)
        print(request_stack)
        stack = list()
        for item in request_stack:
            if item.isalpha():
                stack.append(cls.SearchResult(item.lower()))
                continue

            if item == "!":
                e = stack.pop()
                e.tokens.pop()
                stack.append(cls.SearchResult(e.dock_ids, is_not=True))
                continue

            a = stack.pop()
            b = stack.pop()

            if item == "&":
                c = a & b

            if item == "|":
                c = b | a

            stack.append(c)
        e = stack.pop()
        return e


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Enter search request ... ")
        exit(0)
    response = SearchEngine.search(sys.argv[1])
    # res_dict = {}
    # for record in response:
    #     print(record)
    #     print("=================")

    for record, rel in response:
        print(record)
        print(rel)
        print("=================")
        # res_dict[record['title']] = record

    # with open(sys.argv[1], 'wb') as f:
    #     import pickle
    #     pickle.dump(res_dict, f)

