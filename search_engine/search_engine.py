import re
from search_engine.utils import get_page_ids_for_termin, get_page_by_id


class SearchResult:

    PAGE_COUNT = 50000

    def __init__(self, data, is_not=False):
        if type(data) == str:
            dock_ids = get_page_ids_for_termin(data)
            if is_not:
                dock_ids = set(range(self.PAGE_COUNT)) - dock_ids
            self.dock_ids = dock_ids

        elif type(data) == set:
            if is_not:
                self.dock_ids = set(range(self.PAGE_COUNT)) - data
            else:
                self.dock_ids = data

    def __and__(self, another):
        return SearchResult(self.dock_ids & another.dock_ids)

    def __or__(self, another):
        return SearchResult(self.dock_ids | another.dock_ids)

    def __iter__(self):
        docks = []
        if self.dock_ids:
            docks = [get_page_by_id(dock_id) for dock_id in self.dock_ids]
        print(f"Fount {len(docks)} documents")
        return iter(docks)


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
    def search(request: str) -> SearchResult:
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Enter search request ... ")
        exit(0)
    response = SearchEngine.search(sys.argv[1])
    res_dict = {}
    for record in response:
        print(record)
        res_dict[record['title']] = record

    with open(sys.argv[1], 'wb') as f:
        import pickle
        pickle.dump(res_dict, f)
