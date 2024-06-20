import argparse
import os
import sys
import time
from PIL import Image
import imagehash
import matplotlib.pyplot as plt
import loguru


def time_logger(function):
    def wrapped(*args):
        start_time = time.time()
        res = function(*args)
        loguru.logger.info(f'Время выполнения: {time.time() - start_time}')
        return res

    return wrapped


def is_file_extension_suitable(file_name):
    formats = ['jpg', 'jpeg', 'png', 'gif']
    for file_format in formats:
        if file_name.endswith(file_format):
            return True

    return False


@time_logger
def find_duplicates(paths):
    hash_to_paths = {}

    for path in paths:
        for address, dirs, files in os.walk(str(path)):
            for file_name in files:
                if is_file_extension_suitable(file_name):
                    with Image.open(os.path.join(address, file_name)) as image:
                        image.draft(mode="RGB",
                                    size=(256, 256))  # рескейлим картинку во время чтения (работает только для jpeg)
                        hash_str = str(imagehash.phash(image))
                        if hash_str in hash_to_paths.keys():
                            hash_to_paths[hash_str].append(str(os.path.join(address, file_name)))
                        else:
                            hash_to_paths[hash_str] = [str(os.path.join(address, file_name))]

    return hash_to_paths


def show_duplicates(hash_to_paths, min_len_of_duplicates_groups):
    for hash_str, paths in hash_to_paths.items():
        if len(paths) >= min_len_of_duplicates_groups:
            for i, path in enumerate(paths):
                ax = plt.subplot(1, len(paths), i + 1)
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                img = Image.open(path)
                plt.imshow(img)
                plt.grid()

            plt.show()
            time.sleep(1)

            print("hash: " + hash_str + "\tpaths:" + ", ".join(paths))


def parse_arguments():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser()
    parser.add_argument('--group-len', default=3, type=int)
    parser.add_argument('--paths-list', type=list_of_strings)
    return parser.parse_args()


def main():
    args = parse_arguments()
    show_duplicates(find_duplicates(args.paths_list), args.group_len)


if __name__ == '__main__':
    main()
