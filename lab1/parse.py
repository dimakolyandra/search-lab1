import os
import re
import pprint
import json
import mwparserfromhell
from xml.etree import ElementTree


error_counter = 0
success_counter = 0
file_dir = os.path.dirname(os.path.realpath('__file__'))

def get_need_categories():
    cats = set()
    for cat in open("categories/categories.txt"):
        cats.add(cat.strip())
    return cats


def get_categories(page):
    global error_counter
    result = []
    try:
        result = re.findall(r'\[\[(Категория:[а-яА-Я 0-9]+)\]\]', page)
    except Exception:
        print("Error")
        with open(f"error-{error_counter}.txt", "a+") as f:
            f.write(page)
        error_counter += 1
    return result


def read_xml(file, need_cats):
    global success_counter
    stats_dict = dict()
    text_counter = 1
    with open(file) as read:
        with open("result-pages-pretty.txt", "a+") as write:
            text = title = None

            for _, elem in ElementTree.iterparse(read):
                if "title" in elem.tag:
                    title = elem.text
                if "text" in elem.tag:
                    text = elem.text

                if title is not None and text is not None:
                    text_counter += 1
                    page_cats = get_categories(text)
                    for cat in page_cats:
                        if cat in need_cats:
                            code = mwparserfromhell.parse(text)
                            text = code.strip_code()    
                            success_counter += 1
                            print(f"Succes pages: {success_counter} from {text_counter}")
                            write.write("="*10 + "START_PAGE" + "="*10 + "\n")
                            write.write("+"*10 + "START_PAGE_TITLE" + "+"*10 + "\n")
                            write.write(title + "\n")
                            write.write("+"*10 + "END_PAGE_TITLE" + "+"*10 + "\n")
                            write.write("+"*10 + "START_PAGE_TEXT" + "+"*10 + "\n")
                            write.write(text + "\n")
                            write.write("+"*10 + "END_PAGE_TEXT" + "+"*10 + "\n")
                            write.write("="*10 + "END_PAGE" + "="*10 + "\n")
                    text = title = None

                if text_counter % 50000 == 0:
                    print(f"Parsed: {text_counter} pages")
                    text_counter += 1
                
                if success_counter == 50000:
                    break

                elem.clear()


if __name__ == "__main__":
    cats = get_need_categories()
    print("FOUND CATS: " + str(len(cats)))
    read_xml("ruwiki-latest-pages-articles.xml", cats)
