import os
import urllib.request

import imagehash
import loguru
from PIL import Image
import matplotlib.pyplot as plt
import time
from . import time_logger


class ImagesDuplicateFinder:
    def __init__(self):
        self.__hash_to_paths = {}

    @property
    def hash_to_paths(self):
        return self.__hash_to_paths

    @staticmethod
    def __is_file_extension_suitable(file_name):
        formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        for file_format in formats:
            if file_name.endswith(file_format):
                return True

        return False

    # @time_logger.time_logger
    def group_duplicate(self, paths):
        for path in paths:
            for address, dirs, files in os.walk(str(path)):
                for file_name in files:
                    if self.__is_file_extension_suitable(file_name):
                        try:
                            image = Image.open(os.path.join(address, file_name))
                            image.verify()
                        except IOError as e:
                            loguru.logger.error(f'Error while open or verifying {file_name}')
                            continue

                        # re-open the image after verification, because image equal None after verify method
                        with Image.open(os.path.join(address, file_name)) as image:
                            # rescaling the image while decoding (works only for jpeg)
                            image.draft(mode="RGB", size=(256, 256))

                            hash_str = str(imagehash.phash(image))
                            if hash_str in self.__hash_to_paths.keys():
                                self.__hash_to_paths[hash_str].append(str(os.path.join(address, file_name)))
                            else:
                                self.__hash_to_paths[hash_str] = [str(os.path.join(address, file_name))]

    @staticmethod
    def __display_duplicate_group(paths, hash_str):
        for i, path in enumerate(paths):
            ax = plt.subplot(1, len(paths), i + 1)
            plt.suptitle(f"Группа изображений с одинаковой хэш суммой: {hash_str}")
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            img = Image.open(path)
            plt.imshow(img)
            plt.grid()

        plt.show()

        time.sleep(1)

    def show_duplicates(self, min_len_of_duplicates_groups=3, display_images=False):
        for hash_str, paths in self.__hash_to_paths.items():
            if len(paths) >= min_len_of_duplicates_groups:
                if display_images:
                    try:
                        self.__display_duplicate_group(paths, hash_str)
                    except Exception as e:
                        loguru.logger.error(f'Error while displaying {hash_str}: {e}')

                print("hash: " + hash_str + "\tpaths:" + ", ".join(paths))
