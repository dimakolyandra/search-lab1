import requests
import pickle
from collections import deque

sess = requests.Session()
URL = "https://ru.wikipedia.org/w/api.php"

def _get_wiki_subcat(subcat):
    PARAMS = {
        "action":"query",
        "format":"json",
        "list":"categorymembers",
        "cmtitle": f"{subcat}",
        "cmtype": "subcat"
    }
    resp = sess.get(url=URL, params=PARAMS)
    data = resp.json()
    return [sub["title"] for sub in data['query']['categorymembers']]


def get_subcat(cat):
    categories_set = set()
    que = deque(_get_wiki_subcat(cat))
    with open("categories.txt", "a+") as f:
        while len(que) > 0:
            subcat = que.popleft()
            if subcat not in categories_set:
                categories_set.add(subcat)
                f.write(subcat + "\n")
                f.flush()
                print("Количество подкатегорий: " + str(len(categories_set)))
            que.extend(_get_wiki_subcat(subcat))
    return categories_set


if __name__ == "__main__":
    import pprint
    categories_set = get_subcat("Категория:История")
    print("Количество категорий: " + len(categories_set))
    pickle.dump(categories_set, open("categories.pickle"))
