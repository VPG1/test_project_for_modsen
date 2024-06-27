import os
import shutil
import pytest
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder
import numpy
from PIL import Image


@pytest.fixture(scope='session')
def setup():
    # Delete the directory with tests
    shutil.rmtree('tests_im', ignore_errors=True)

    # Random image generation
    imarray1 = numpy.random.rand(100, 100, 3) * 255
    im1 = Image.fromarray(imarray1.astype('uint8')).convert('RGBA')

    imarray2 = numpy.random.rand(100, 100, 3) * 255
    im2 = Image.fromarray(imarray2.astype('uint8')).convert('RGBA')

    imarray3 = numpy.random.rand(100, 100, 3) * 255
    im3 = Image.fromarray(imarray3.astype('uint8')).convert('RGBA')

    os.mkdir('tests_im')

    # Initialization directory for the first test
    os.mkdir('tests_im/test1')
    im1.save('tests_im/test1/result_image1.png')
    im2.save('tests_im/test1/result_image2.png')
    im3.save('tests_im/test1/result_image3.png')

    # Initialization directory for the second test
    os.mkdir('tests_im/test2')
    im1.save('tests_im/test2/result_image1.png')
    im1.save('tests_im/test2/result_image2.png')
    im2.save('tests_im/test2/result_image3.png')

    # Initialization directory for the third test
    os.mkdir('tests_im/test3_1')
    im1.save('tests_im/test3_1/result_image1.png')
    im2.save('tests_im/test3_1/result_image2.png')

    os.mkdir('tests_im/test3_2')
    im1.save('tests_im/test3_2/result_image3.png')
    im3.save('tests_im/test3_2/result_image4.png')

    yield

    # Delete the directory with test data
    shutil.rmtree('tests_im', ignore_errors=True)


@pytest.mark.usefixtures('setup')
class TestImagesDuplicateFinder:
    @pytest.mark.parametrize(
        "paths, result",
        [
            (['tests_im/test1'], 3),  # All images are different
            (['tests_im/test2'], 2),  # Two identical images
            (['tests_im/test3_1', 'tests_im/test3_2'], 3),  # Two identical images in different folders
            (['a', 'b', 'c'], 0),  # Non-existent directories
        ]
    )
    def test_group_duplicate(self, paths, result):
        duplicate_finder = ImagesDuplicateFinder(group_by_feature=False)
        duplicate_finder.load_images(paths)
        duplicate_finder.group_duplicates()
        assert len(duplicate_finder.hash_to_paths) == result
