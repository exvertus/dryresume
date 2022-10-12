import pytest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from dryresume.resume import Resume, year_only, in_groups_of

PARENT_1_VALUE, PARENT_2_VALUE = str(uuid4()), str(uuid4())
FAKE_DIR = '/fake/temp/dir'
TEST_DATA = {
    'parent.json': {
        "resume": PARENT_1_VALUE,
        "options": {}
    },
    'child.json': {
        "options": {
            "parent-data": "./parent.json"
        }
    },
    'grandchild.json': {
        "options": {
            "parent-data": "./child.json"
        }
    },
    'parentTwo.json': {
        "resume": PARENT_2_VALUE,
        "options": {}
    },
    'childTwo.json': {
        "options": {
            "parent-data": "./parentTwo.json"
        }
    },
    'childTwoAgain.json': {
        "options": {
            "parent-data": "./parentTwo.json"
        }
    }
}

test_dates = {
    '01/01/1000': '1000',
    '07/04/1776': '1776',
    '10/31/2022': '2022'
}
@pytest.mark.parametrize("td", test_dates)
def test_year_only(td):
    assert year_only(td) == test_dates[td]

test_lengths = ((0, 0), (8, 1), (7, 3), (30, 7))
@pytest.mark.parametrize("tl", test_lengths)
def test_in_groups_of(tl):
    testlist = ["a"*tl[0]]
    assert len(in_groups_of(testlist, tl[1])) == tl[1]

class TestResume:
    @pytest.fixture(scope='class', autouse=True)
    def fake_fs(self, fs_module):
        return fs_module

    def test_get_config_missing(self, fs):
        arbitrary_path = Path(str(uuid4()))
        with pytest.raises(FileNotFoundError):
            Resume(arbitrary_path, None)

    @pytest.fixture(scope='class')
    def stub_reader(self, class_mocker):
        def se(arg):
            """use filepath as key to expected dict"""
            key = Path(arg.name).name
            return TEST_DATA[key]

        reader = class_mocker.Mock(name='reader')
        reader.side_effect = se
        return reader

    @pytest.fixture(params=TEST_DATA.keys())
    def fake_file(self, fake_fs, request):
        path = Path(FAKE_DIR) / request.param
        fake_fs.create_file(path)
        return path

    @pytest.fixture()
    def resume_obj(self, stub_reader, fake_file):
        return Resume(fake_file, stub_reader)

    def test_load_config(self, resume_obj, fake_file):
        if resume_obj.config_file.name in \
            ('parent.json', 'child.json', 'grandchild.json'):
            assert resume_obj.data == PARENT_1_VALUE
        elif resume_obj.config_file.name in \
            ('parentTwo.json', 'childTwo.json', 'childTwoAgain.json'):
            assert resume_obj.data == PARENT_2_VALUE
