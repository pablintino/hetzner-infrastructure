import pytest
import os

from fs.temporal_fs_manager import TemporalFsManager


@pytest.fixture
def fs_manager():
    fs_man = TemporalFsManager()
    yield fs_man
    fs_man.cleanup()


def test_get_temporal_directory_ok(fs_manager):
    dir = fs_manager.get_temporal_directory()
    assert dir
    assert os.path.exists(dir)


def test_get_temporal_file_ok(fs_manager):
    file = fs_manager.get_temporal_file()
    assert file
    assert os.path.exists(file)
