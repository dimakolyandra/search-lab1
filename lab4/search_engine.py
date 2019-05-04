from utils import get_page_ids_for_termin, get_page_by_id


class SearchEngine:

    class SearchResult:

        def __init__(self, data):
            if type(data) == str:
                self.dock_ids = get_page_ids_for_termin(data)

            elif type(data) == set:
                self.dock_ids = data

        def __and__(self, another):
            return SearchEngine.SearchResult(self.dock_ids & another.dock_ids)

        def __or__(self, another):
            return SearchEngine.SearchResult(self.dock_ids | another.dock_ids)

        def __iter__(self):
            docks = [get_page_by_id(dock_id) for dock_id in self.dock_ids]
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
            for c in request:
                if prev == ' ' and c == ' ':
                    continue
                result_request.append(c)
                prev = c
            return (''.join(result_request).strip()
                      .replace(' ', '&')
                      .replace('&&', '&')
                      .replace('||', '|'))

    @classmethod
    def search(cls, request: str) -> SearchResult:
        request_stack = cls.SearchRequest.get_request(request)
        stack = list()
        for item in request_stack:
            if item.isalpha():
                stack.append(cls.SearchResult(item))
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
    for record in response:
        print(record)
