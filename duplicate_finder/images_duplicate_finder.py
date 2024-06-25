import os
import imagehash
import loguru
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
# import multiprocessing

from keras.src.applications.vgg16 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow import keras


class ImagesDuplicateFinder:
    def __init__(self, group_by_feature=True):
        self.__model = None
        if group_by_feature:
            loguru.logger.info('Initializing ImagesDuplicateFinder...')
            self.__model = keras.applications.VGG16 (weights='imagenet', include_top=False,
                                                    pooling='max', input_shape=(224, 224, 3))
            for model_layer in self.__model.layers:
                model_layer.trainable = False

        self.__images = []
        self.__hash_to_paths = {}
        self.__features_list = []
        self.__images_grouped_by_features = []

    @property
    def hash_to_paths(self):
        """Геттер для словаря с дубликатами по хэшам"""
        return self.__hash_to_paths

    def load_images(self, paths):
        """Метод для загрузки изображений"""
        for path in paths:
            for address, dirs, files in os.walk(str(path)):
                for file_name in files:
                    if self.__is_file_extension_suitable(file_name):
                        try:
                            with Image.open(os.path.join(address, file_name)) as image:
                                image.verify()
                        except IOError as e:
                            loguru.logger.error(f'Error while open or verifying {file_name}')
                            continue

                        image = Image.open(os.path.join(address, file_name))
                        self.__images.append((os.path.join(address, file_name), image))

    @staticmethod
    def __is_file_extension_suitable(file_name):
        """Метод для проверки расширения файлов"""
        formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        for file_format in formats:
            if file_name.endswith(file_format):
                return True

        return False

    @staticmethod
    def __calculate_hash(image):
        return str(imagehash.phash(image))

    def __calculate_features_vector(self, image):
        resized_image = image.resize((224, 224))
        img_array = np.expand_dims(np.array(resized_image), axis=0)
        img_array = preprocess_input(img_array)
        return self.__model.predict(img_array).flatten()

    # @time_logger.time_logger
    def group_duplicates(self):
        """Метод для группировки дубликатов"""

        # with multiprocessing.Pool() as pool:
        #     pool.map(self.__calculate_hash, self.__images)
        # группируем по хэшу
        for path, image in self.__images:
            hash_str = self.__calculate_hash(image)

            if hash_str in self.__hash_to_paths.keys():
                self.__hash_to_paths[hash_str].append((path, image))
            else:
                self.__hash_to_paths[hash_str] = [(path, image)]

        if self.__model is not None:
            # группируем по признакам
            for path, image in self.__images:
                features_vector = self.__calculate_features_vector(image)
                self.__features_list.append(features_vector)

            similarity_matrix = cosine_similarity(self.__features_list)

            for i in range(len(similarity_matrix)):
                duplicates = [self.__images[i]]
                for j in range(i + 1, len(similarity_matrix)):
                    if similarity_matrix[i, j] > 0.9:
                        duplicates.append(self.__images[j])

                self.__images_grouped_by_features.append(duplicates)

    @staticmethod
    def __display_duplicate_group(group, message):
        """Метод для вывода на экран группы изображений"""
        for i, image in enumerate(group):
            ax = plt.subplot(1, len(group), i + 1)
            plt.suptitle(message)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            plt.imshow(image[1])
            plt.grid()

        plt.show()

        time.sleep(1)

    def show_duplicates(self, min_len_of_duplicates_groups=3, display_images=False):
        """Метод для вывода всех групп дубликатов"""
        print("Группы по хэшам:")
        for i, group in enumerate(self.__hash_to_paths.values()):
            if len(group) >= min_len_of_duplicates_groups:
                if display_images:
                    self.__display_duplicate_group(group, f"Группа {i + 1}.(По хэшам)")
                print([img[0] for img in group])

        print("Группы по признакам:")
        for i, group in enumerate(self.__images_grouped_by_features):
            if len(group) >= min_len_of_duplicates_groups:
                if display_images:
                    self.__display_duplicate_group(group, f"Группа {i + 1}.(По признакам)")
                print([img[0] for img in group])
