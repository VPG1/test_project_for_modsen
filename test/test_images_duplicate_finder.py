import os
import shutil
import pytest
from src.duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder
import numpy
from PIL import Image


@pytest.fixture(scope='session')
def setup():
    # удаляем директорию с тестами
    shutil.rmtree('tests_im', ignore_errors=True)

    # генерация рандомных изображений
    imarray1 = numpy.random.rand(100, 100, 3) * 255
    im1 = Image.fromarray(imarray1.astype('uint8')).convert('RGBA')

    imarray2 = numpy.random.rand(100, 100, 3) * 255
    im2 = Image.fromarray(imarray2.astype('uint8')).convert('RGBA')

    imarray3 = numpy.random.rand(100, 100, 3) * 255
    im3 = Image.fromarray(imarray3.astype('uint8')).convert('RGBA')

    os.mkdir('tests_im')

    # инициализация директория для первого теста
    os.mkdir('tests_im/test1')
    im1.save('tests_im/test1/result_image1.png')
    im2.save('tests_im/test1/result_image2.png')
    im3.save('tests_im/test1/result_image3.png')

    # инициализация директория для второго теста
    os.mkdir('tests_im/test2')
    im1.save('tests_im/test2/result_image1.png')
    im1.save('tests_im/test2/result_image2.png')
    im2.save('tests_im/test2/result_image3.png')

    # инициализация директорий для третьего теста
    os.mkdir('tests_im/test3_1')
    im1.save('tests_im/test3_1/result_image1.png')
    im2.save('tests_im/test3_1/result_image2.png')

    os.mkdir('tests_im/test3_2')
    im1.save('tests_im/test3_2/result_image3.png')
    im3.save('tests_im/test3_2/result_image4.png')

    yield

    # удаляем директорию с данными для тестов
    shutil.rmtree('tests_im', ignore_errors=True)


@pytest.mark.usefixtures('setup')
class TestImagesDuplicateFinder:
    @pytest.mark.parametrize(
        "paths, result",
        [
            (['tests_im/test1'], 3),  # все изображения разные
            (['tests_im/test2'], 2),  # два одинаковых изображения
            (['tests_im/test3_1', 'tests_im/test3_2'], 3),  # два одинаковы изображения в разных папках
            (['a', 'b', 'c'], 0),  # несуществующие директории
        ]
    )
    def test_group_duplicate(self, paths, result):
        duplicate_finder = ImagesDuplicateFinder(group_by_feature=False)
        duplicate_finder.load_images(paths)
        duplicate_finder.group_duplicates()
        assert len(duplicate_finder.hash_to_paths) == result
