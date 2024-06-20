import argparse
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder


def parse_arguments():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser()
    parser.add_argument('--group-len', default=3, type=int)
    parser.add_argument('--paths-list', type=list_of_strings)
    return parser.parse_args()


def main():
    args = parse_arguments()
    duplicate_finder = ImagesDuplicateFinder()
    duplicate_finder.group_duplicate(args.paths_list)
    duplicate_finder.show_duplicates(args.group_len, display_images=True)


if __name__ == '__main__':
    main()
