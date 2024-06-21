import argparse
import os.path
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder


def parse_arguments():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser()
    parser.add_argument('--group-len', default=3, type=int)
    parser.add_argument('--paths-list', type=list_of_strings)
    parser.add_argument('--display-images', default=True, type=bool)

    args = parser.parse_args()

    if args.paths_list is None:
        print("You must provide paths")
        exit()
    for path in args.paths_list:
        if not os.path.isdir(path):
            print("One of the paths is incorrect")
            exit()
    return args


def main():
    args = parse_arguments()

    duplicate_finder = ImagesDuplicateFinder()
    duplicate_finder.group_duplicate(args.paths_list)
    duplicate_finder.show_duplicates(args.group_len, display_images=True)


if __name__ == '__main__':
    main()
