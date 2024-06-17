import argparse
import os
import sys
from PIL import Image
import imagehash


def is_file_extension_suitable(file_name):
    formats = ['jpg', 'jpeg']
    for file_format in formats:
        if file_name.endswith(file_format):
            return True

    return False


def find_duplicates(paths):
    hash_to_paths = {}

    for path in paths:
        for address, dirs, files in os.walk(str(path)):
            for file_name in files:
                if is_file_extension_suitable(file_name):
                    hash_str = str(imagehash.whash(Image.open(os.path.join(path, file_name))))
                    if hash_str in hash_to_paths.keys():
                        hash_to_paths[hash_str].append(str(os.path.join(path, file_name)))
                    else:
                        hash_to_paths[hash_str] = [str(os.path.join(path, file_name))]

    return hash_to_paths


def print_duplicates(hash_to_paths):
    for hash_str, paths in hash_to_paths.items():
        if len(paths) > 2:
            print("hash: " + hash_str + "\tpaths:" + ", ".join(paths))


def main():
    if len(sys.argv) <= 1:
        print("paths must be specified as an argument")
        return

    print_duplicates(find_duplicates(sys.argv[1:]))


if __name__ == '__main__':
    main()
