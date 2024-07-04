import pytest
from duplicate_finder.images_duplicate_finder import ImagesDuplicateFinder
from setup import setup


@pytest.mark.usefixtures('setup')
class TestGroupDuplicate:
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
        duplicate_finder.group_duplicates(False)
        assert len(duplicate_finder.hash_to_paths) == result

    @pytest.mark.parametrize(
        "paths, result",
        [
            (['tests_im/test1'], 3),  # All images are different
            (['tests_im/test2'], 2),  # Two identical images
            (['tests_im/test3_1', 'tests_im/test3_2'], 3),  # Two identical images in different folders
        ]
    )
    def test_group_duplicate_multiprocessing(self, paths, result):
        duplicate_finder = ImagesDuplicateFinder(group_by_feature=False)
        duplicate_finder.load_images(paths)
        duplicate_finder.group_duplicates(True)
        assert len(duplicate_finder.hash_to_paths) == result
