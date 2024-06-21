import os
import imagehash
from PIL import Image
import matplotlib.pyplot as plt
import time
from . import time_logger


class ImagesDuplicateFinder:
    def __init__(self):
        self.__hash_to_paths = {}

    @staticmethod
    def __is_file_extension_suitable(file_name):
        formats = ['jpg', 'jpeg', 'png', 'gif']
        for file_format in formats:
            if file_name.endswith(file_format):
                return True

        return False

    @time_logger.time_logger
    def group_duplicate(self, paths):
        for path in paths:
            for address, dirs, files in os.walk(str(path)):
                for file_name in files:
                    if self.__is_file_extension_suitable(file_name):
                        with Image.open(os.path.join(address, file_name)) as image:
                            # рескейлим картинку во время чтения (работает только для jpeg)
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
                    self.__display_duplicate_group(paths, hash_str)

                print("hash: " + hash_str + "\tpaths:" + ", ".join(paths))