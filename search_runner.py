from argparse import ArgumentParser

from search_engine.search_engine import SearchEngine as search_bool
from search_engine_tf_idf.search_engine import SearchEngine as search_tf_idf
from builder_utils import init_environ, run_test_for_stage, init_logging


def _init_argparser() -> ArgumentParser:
    text = "Script for ruling indexation process." \
           "Data structure in config.yml, input file with name data.in"
    parser = ArgumentParser(description=text)
    parser.add_argument(
        "--range", "-r",
        help=f"Use tf-idf search engine",
        action="store_true")
    parser.add_argument(
        "--tests", "-t",
        help="Run tests for boolean search engine",
        action="store_true")
    parser.add_argument("--loglvl", "-l", help=f"Logging level")
    return parser


def do_search_circle(SearchEngine):
    while True:
        request = input("Enter search request, or exit: ")
        if request == "exit":
            print("Good By!")
            break
        response = SearchEngine.search(request)
        for record in response:
            if type(record) == tuple:
                print(record[0])
                print(record[1])
            else:
                print(record)
            cmd = input("...")
            if cmd == "break":
                break
        print("\n" * 5)


if __name__ == "__main__":
    init_environ(__file__)
    args = _init_argparser().parse_args()
    init_logging(args.loglvl)
    engine = search_tf_idf if args.range else search_bool
    if args.tests:
        run_test_for_stage("search_engine")
    else:
        do_search_circle(engine)
