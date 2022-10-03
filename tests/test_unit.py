import pytest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from resume_automator.data_manager import ResumeData

class TestResumeData:
    def test_get_config_missing(self, fs):
        arbitrary_path = Path(str(uuid4()))
        with pytest.raises(FileNotFoundError):
            ResumeData(arbitrary_path, None)

    @pytest.fixture(scope='class')
    def resume_instance(self, fs):
        pass

    def test_load_config_parent(self):
        assert "this" == "isn't finished"

    def test_load_config_children(self):
        assert "this" == "isn't finished"
    