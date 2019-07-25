import os
import pickle


INPUT_DATA_DIR = './tokens_data'
OUTPUT_DATA_DIR = './tokens_prepared'


def save_not_sorted_dict():
    file_names = os.listdir(INPUT_DATA_DIR)
    digit_values = list()
    with open(os.path.join(OUTPUT_DATA_DIR, 'inverse_not_sorted.txt'), 'w') as f:
        for file in file_names:
            tokens = pickle.load(open(os.path.join(INPUT_DATA_DIR, file), 'rb'))
            for _, val in tokens.items():
                for token in val['tokens']:
                    try:
                        token_val = int(token[0])
                        digit_str = str(token_val) + "\t" + str(val['id']) + ":" + str(token[1]) + "\n"
                        digit_values.append(digit_str)
                        print(len(digit_values))
                        continue
                    except ValueError:
                        token_val = token[0].lower()
                    f.write(str(token_val) + "\t" + str(val['id']) + ":" + str(token[1]) + "\n")

    with open(os.path.join(OUTPUT_DATA_DIR, 'digits.txt'), 'w') as f:
        digit_values = sorted(digit_values, key=lambda x: int(x.split('\t')[0]))
        for val in digit_values:
            f.write(val)


if __name__ == "__main__":
    save_not_sorted_dict()
    # with open(os.path.join(OUTPUT_DATA_DIR, 'sorted_2.txt'), 'a') as f1, \
    #      open(os.path.join(OUTPUT_DATA_DIR, 'digits.txt')) as f2:
    #     for line in f2:
    #         f1.write(line)
