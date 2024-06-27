import os
from multiprocessing import Pool, cpu_count

import imagehash
import loguru
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from keras.src.applications.vgg16 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow import keras


class ImagesDuplicateFinder:
    def __init__(self, group_by_feature):
        self.__model = None
        if group_by_feature:
            # Initializing Model
            loguru.logger.info('Initializing Model...')
            self.__model = keras.applications.VGG16(weights='imagenet', include_top=False,
                                                    pooling='max', input_shape=(224, 224, 3))
            for model_layer in self.__model.layers:
                model_layer.trainable = False

        self.__images_paths = []
        self.__hash_to_paths = {}
        self.__features_list = []
        self.__images_grouped_by_features = []

    @property
    def hash_to_paths(self):
        """Getter for a dictionary with duplicates by hashes"""
        return self.__hash_to_paths

    def load_images(self, paths):
        """Method for loading images"""
        for path in paths:
            for address, dirs, files in os.walk(str(path)):
                for file_name in files:
                    if self.__is_file_extension_suitable(file_name):
                        try:
                            with Image.open(os.path.join(address, file_name)) as image:
                                image.verify()
                        except IOError:
                            loguru.logger.error(f'Error while open or verifying {file_name}')
                            continue

                        self.__images_paths.append(os.path.join(address, file_name))

    @staticmethod
    def __is_file_extension_suitable(file_name):
        """Method for checking file extensions"""
        formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        for file_format in formats:
            if file_name.endswith(file_format):
                return True

        return False

    def __calculate_features_vector(self, path):
        """Method for calculating the vector of image features"""
        with Image.open(path) as image:
            resized_image = image.resize((224, 224))
            img_array = np.expand_dims(np.array(resized_image), axis=0)
            img_array = preprocess_input(img_array)
            return self.__model.predict(img_array).flatten()

    # Can’t make method private, because we can’t call private methods from other processes
    @staticmethod
    def _calculate_hash(path):
        """Method to calculate image hash"""
        with Image.open(path) as image:
            return str(imagehash.phash(image))

    # @time_logger.time_logger
    def group_duplicates(self, multiprocessing_on):
        """Method for grouping duplicates"""
        # Grouping by hash
        if multiprocessing_on:  # Calculate hashes in all threads
            with Pool(cpu_count()) as pool:
                hashes = pool.map(self._calculate_hash, self.__images_paths)

            for i, hash_str in enumerate(hashes):
                if hash_str in self.__hash_to_paths:
                    self.__hash_to_paths[hash_str].append(self.__images_paths[i])
                else:
                    self.__hash_to_paths[hash_str] = [self.__images_paths[i]]
        else:  # Calculate hashes in one thread
            for path in self.__images_paths:
                hash_str = self._calculate_hash(path)

                if hash_str in self.__hash_to_paths.keys():
                    self.__hash_to_paths[hash_str].append(path)
                else:
                    self.__hash_to_paths[hash_str] = [path]

        if self.__model is not None:
            # Grouping by features
            for path in self.__images_paths:
                features_vector = self.__calculate_features_vector(path)
                self.__features_list.append(features_vector)

            similarity_matrix = cosine_similarity(self.__features_list)

            for i in range(len(similarity_matrix)):
                duplicates = [self.__images_paths[i]]
                for j in range(i + 1, len(similarity_matrix)):
                    if similarity_matrix[i, j] > 0.9:
                        duplicates.append(self.__images_paths[j])

                self.__images_grouped_by_features.append(duplicates)

    @staticmethod
    def __display_duplicate_group(group, message):
        """Method for displaying a group of images"""
        plt.clf()
        for i, path in enumerate(group):
            ax = plt.subplot(1, len(group), i + 1)
            plt.suptitle(message)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            with Image.open(path) as image:
                plt.imshow(image)
            plt.grid()

        plt.show()

        plt.draw()
        plt.gcf().canvas.flush_events()

    def show_duplicates(self, min_len_of_duplicates_groups, display_images):
        """Method for outputting all groups of duplicates"""
        # Enable interactive mode
        plt.ion()

        i = 1
        print("Group by hash:")
        # Displaying groups by hash
        for group in self.__hash_to_paths.values():
            if len(group) >= min_len_of_duplicates_groups:
                if display_images:
                    self.__display_duplicate_group(group, f"Group {i}.(by hash)")

                print(f"Group {i}:")
                for path in group:
                    print(path)

                i += 1
                plt.pause(1)

        # Displaying groups by features
        if self.__model is not None:
            i = 1
            print("Group by features:")
            for group in self.__images_grouped_by_features:
                if len(group) >= min_len_of_duplicates_groups:
                    if display_images:
                        self.__display_duplicate_group(group, f"Group {i}.(by features)")

                    print(f"Group {i}:")
                    for path in group:
                        print(path)

                    i += 1
                    plt.pause(1)
