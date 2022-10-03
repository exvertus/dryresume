import pytest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from resume_automator.data_manager import ResumeData

@pytest.fixture()
def fake_empty_file(fs):
    fp = Path('/fake/file.json')
    fs.create_file(fp)
    return fp

@pytest.fixture()
def mock_reader(mocker):
    return mocker.Mock(name='reader', return_value={"data": []})

@pytest.fixture()
def parent_instance(fake_empty_file, mock_reader):
    return ResumeData(fake_empty_file, mock_reader)

class TestResumeData:
    def test_get_config_missing(self, fs):
        arbitrary_path = Path(str(uuid4()))
        with pytest.raises(FileNotFoundError):
            ResumeData(arbitrary_path, None)

    def test_load_config_parent(self, parent_instance, mock_reader):
        assert parent_instance.data == mock_reader.return_value

    # def test_load_config_children(self):
    #     assert "this" == "isn't finished"