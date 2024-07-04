import pytest
from setup import setup
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder


@pytest.mark.usefixtures('setup')
class TestLoadImages:
    @pytest.mark.parametrize(
        "paths, result",
        [
            (['tests_im/test1'], 3),  # All images are different
            (['tests_im/test2'], 3),  # Two identical images
            (['tests_im/test3_1', 'tests_im/test3_2'], 4),  # Two identical images in different folders
            (['a', 'b', 'c'], 0),  # Non-existent directories
        ]
    )
    def test_load_images(self, paths, result):
        duplicate_finder = ImagesDuplicateFinder(group_by_feature=False)
        duplicate_finder.load_images(paths)
        assert len(duplicate_finder.images_paths) == result
