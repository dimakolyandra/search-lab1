import os
import re
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


def write_to_file(file, title, success_counter, text_counter, text):
    print(f"Succes page: {success_counter} from {text_counter}")
    file.write("=" * 10 + "START_PAGE" + "=" * 10 + "\n")
    file.write("+" * 10 + "START_PAGE_TITLE" + "+" * 10 + "\n")
    file.write(title + "\n")
    file.write("+" * 10 + "END_PAGE_TITLE" + "+" * 10 + "\n")
    file.write("+" * 10 + "START_PAGE_TEXT" + "+" * 10 + "\n")
    file.write(text + "\n")
    file.write("+" * 10 + "END_PAGE_TEXT" + "+" * 10 + "\n")
    file.write("=" * 10 + "END_PAGE" + "=" * 10 + "\n")


def read_xml(file, need_cats):
    global success_counter
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
                            write_to_file(
                                write, title,
                                success_counter, text_counter, text)
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
