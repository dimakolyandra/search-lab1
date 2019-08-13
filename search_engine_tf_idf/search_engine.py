import re
from math import log
from builder_utils import get_page_ids_for_termin, get_page_by_id


class SearchResult:

    PAGE_COUNT = 50000
    iter_counter = 0

    def __init__(self, data, is_not=False):
        if type(data) == str:
            dock_ids = get_page_ids_for_termin(data, with_tf_df=True)
            if is_not:
                ids = self._get_dock_ids(dock_ids)
                ids = set(range(self.PAGE_COUNT)) - ids
                self.dock_ids = filter(lambda x: x[0] in ids, dock_ids)
            self.dock_ids = dock_ids

        elif type(data) == set:
            if is_not:
                ids = set(range(self.PAGE_COUNT)) - self._get_dock_ids(data)
                self.dock_ids = filter(lambda x: x[0] in ids, data)
            else:
                self.dock_ids = data

    def _get_dock_ids(self, docks=None):
        docks = docks or self.dock_ids
        return {dock_id for dock_id, _, _ in docks}

    def __and__(self, another):
        dock_ids = self._get_dock_ids() & another._get_dock_ids()
        return SearchResult(
            set(filter(lambda x: x[0] in dock_ids, self.dock_ids)))

    def __or__(self, another):
        dock_ids = self._get_dock_ids() | another._get_dock_ids()
        return SearchResult(
            set(filter(lambda x: x[0] in dock_ids, self.dock_ids)))

    def __iter__(self):
        print(f"Found {len(self.dock_ids)} pages")
        self.dock_ids_list = [(dock_id, tf * log(self.PAGE_COUNT / df + 1))
                              for dock_id, tf, df in self.dock_ids]
        self.dock_ids_list.sort(key=lambda x: -x[1])
        return self

    def __next__(self):
        if self.iter_counter < len(self.dock_ids_list):
            self.iter_counter += 1
            dock_id, tf_idf = self.dock_ids_list[self.iter_counter]
            return get_page_by_id(dock_id), tf_idf
        raise StopIteration


class SearchRequest:

    PRIORITY = {
        "&": 2,
        "|": 2,
        "(": 1,
        ")": 1,
        "#": -1
    }

    def __init__(self, request: str):
        self.raw_request = request

    def get_request(self) -> list:
        request = self._prepare_request()
        if not self.is_valid(request):
            raise ValueError("Not valid request")
        return self._get_polish_inverse(request)

    def _get_polish_inverse(self, experssion: str) -> list:
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
            elif item in self.PRIORITY.keys():
                if term_buf:
                    result.append(term_buf)
                    term_buf = ''
                while True:
                    stack_head = stack.pop()
                    if self.PRIORITY[stack_head] < self.PRIORITY[item]:
                        stack.append(stack_head)
                        break
                    result.append(stack_head)
                stack.append(item)

        if term_buf:
            result.append(term_buf)

        for i in range(len(stack)):
            result.append(stack[len(stack) - i - 1])

        return result[:-1]

    def is_valid(self, request: str) -> list:
        return True

    def _prepare_request(self) -> str:
        result_request = []
        request = (self.raw_request.replace('(', ' ( ')
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


class SearchEngine:

    @staticmethod
    def search(request: str, only_count: bool) -> SearchResult:
        request_stack = SearchRequest(request).get_request()
        stack = list()
        for item in request_stack:
            if item.isalpha():
                stack.append(SearchResult(item.lower()))
                continue

            if item == "!":
                e = stack.pop()
                stack.append(SearchResult(e.dock_ids, is_not=True))
                continue

            a = stack.pop()
            b = stack.pop()

            if item == "&":
                c = a & b

            if item == "|":
                c = b | a

            stack.append(c)

        return stack.pop()
