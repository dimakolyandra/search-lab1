import pickle
import os
import sys
import math
import matplotlib.pyplot as plt


TOKENS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'data/tokenisation.out')


def get_sorted_freq(tokens_freq):
    tokens_list = [(token, freq) for token, freq in tokens_freq.items()]
    return sorted(tokens_list, key=lambda x: x[1], reverse=True)


def get_plot_data(sorted_tokens):
    return [(rang, freq[1]) for rang, freq in enumerate(sorted_tokens, 1)]


def calc_tcipfa():
    tokens = None
    tokens_set = list()
    tokens_freq = dict()
    with open(TOKENS_PATH, 'rb') as input_:
        tokens = pickle.load(input_)
    for _, value in tokens.items():
        for token, _ in value["tokens"]:
            tokens_set.append(sys.intern(token.lower()))
    del tokens
    for token in tokens_set:
        if token in tokens_freq:
            tokens_freq[token] += 1
        else:
            tokens_freq[token] = 1
    sorted_freq = get_sorted_freq(tokens_freq)
    plot_data = get_plot_data(sorted_freq)

    x_arr = [x for x, _ in plot_data]
    y_arr = [y for _, y in plot_data]
    plt.plot(x_arr, y_arr)
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    plt.title('Закон Ципфа')
    plt.show()

    x_arr = [x for x, _ in plot_data]
    y_arr = [math.log(y) for _, y in plot_data]
    plt.plot(x_arr, y_arr)
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    plt.title('Закон Ципфа с логарифмической шкалой')
    plt.show()


if __name__ == "__main__":
    calc_tcipfa()
