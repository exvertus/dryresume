import pytest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from resume_automator.data_manager import ResumeData

@pytest.fixture()
def fake_files(fs):
    parent = Path('/fake/parent.empty')
    child = parent.parent / 'child.empty'
    grandchild = parent.parent / 'grandchild.empty'
    for f in parent, child, grandchild:
        fs.create_file(f)
    return parent, child, grandchild

@pytest.fixture()
def fake_readers(mocker, fake_files):
    parent = mocker.Mock(
        name='parent_reader', 
        return_value={"data": []})
    child = mocker.Mock(
        name='child_reader', 
        return_value={"parent-data": fake_files[1], "patches": []}
        )
    grandchild = mocker.Mock(
        name='grandchild_reader', 
        return_value={"parent-data": fake_files[2], "patches": []}
        )
    return parent, child, grandchild

@pytest.fixture()
def instances(fake_files, fake_readers):
    # TODO: use side_effect to return different results from same obj.
    parent = ResumeData(fake_files[0], fake_readers[0])
    child = ResumeData(fake_files[1], fake_readers[1])
    grandchild = ResumeData(fake_files[2], fake_readers[2])
    return parent, child, grandchild

class TestResumeData:
    def test_get_config_missing(self, fs):
        arbitrary_path = Path(str(uuid4()))
        with pytest.raises(FileNotFoundError):
            ResumeData(arbitrary_path, None)

    def test_load_config_parent(self, instances, fake_readers):
        assert instances[0].data == fake_readers[0].return_value

    def test_load_config_child(self, instances, fake_readers):
        assert instances[1].data == fake_readers[1].return_value

    def test_load_config_grandchild(self, instances, fake_readers):
        assert instances[2].data == fake_readers[2].return_value
