import argparse
import os.path
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder


def parse_arguments():
    def list_of_strings(arg):
        return arg.split(',')

    parser = argparse.ArgumentParser(
        prog='Duplicate finder',
        description='Finds duplicate images by using and grouping them.',

    )
    parser.add_argument('--group-len', default=3, type=int,
                        help='Group len(default: 3)')
    parser.add_argument('--group_by_features', action=argparse.BooleanOptionalAction,
                        help='If you want to search for duplicates by features')
    parser.add_argument('--display-images', action=argparse.BooleanOptionalAction,
                        help='If you want to display images')
    parser.add_argument('--paths-list', type=list_of_strings,
                        help='List of paths to images')

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
    duplicate_finder = ImagesDuplicateFinder(args.group_by_features)
    duplicate_finder.load_images(args.paths_list)
    duplicate_finder.group_duplicates()
    duplicate_finder.show_duplicates(args.group_len, args.display_images)


if __name__ == '__main__':
    main()
