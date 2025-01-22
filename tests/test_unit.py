import pytest
from pathlib import Path
from uuid import uuid4

from dryresume.resume import Resume, year_and_month, in_groups_of

PARENT_1_VALUE, PARENT_2_VALUE = str(uuid4()), str(uuid4())
FAKE_DIR = '/fake/temp/dir'
TEST_DATA = {
    'parent.json': {
        "resume": PARENT_1_VALUE,
        "options": {
            'output-html': "./parent.html"
        }
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
    '01/01/1000': '01/1000',
    '07/04/1776': '07/1776',
    '10/31/2022': '10/2022'
}
@pytest.mark.parametrize("td", test_dates)
def test_year_only(td):
    assert year_and_month(td) == test_dates[td]

test_lengths = ((0, 0), (8, 1), (7, 3), (30, 7))
@pytest.mark.parametrize("tl", test_lengths)
def test_in_groups_of_len(tl):
    testlist = ["a"*tl[0]]
    assert len(in_groups_of(testlist, tl[1])) == tl[1]

def test_in_groups_of_data():
    testlist = [i for i in range(11)]
    assert in_groups_of(testlist, 3) == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10]]

class TestResume():
    @pytest.fixture(scope='class', autouse=True)
    def mock_jinja(self, class_mocker):
        class_mocker.patch('dryresume.resume.Environment')
        class_mocker.patch('dryresume.resume.PackageLoader')
        class_mocker.patch('dryresume.resume.select_autoescape')

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
    def fake_file(self, fs_session, request):
        p = Path(FAKE_DIR) / request.param
        fs_session.create_file(p)
        return p

    @pytest.fixture()
    def resume_obj(self, stub_reader, fake_file, fs_session):
        return Resume(fake_file, stub_reader)

    def test_load_config(self, resume_obj, fs_session):
        if resume_obj.config_file.name in \
            ('parent.json', 'child.json', 'grandchild.json'):
            assert resume_obj.data == PARENT_1_VALUE
        elif resume_obj.config_file.name in \
            ('parentTwo.json', 'childTwo.json', 'childTwoAgain.json'):
            assert resume_obj.data == PARENT_2_VALUE

    def test_to_html(self, fs_session, mock_jinja, mocker, stub_reader):
        test_path = Path(FAKE_DIR) / 'parent.json'
        if not test_path.exists():
            fs_session.create_file(test_path)
        fs_session.add_real_directory(
            Path(__file__).parent.parent / 'dryresume' / 'templates')
        class JinjaTemplate(object):
            def render(self, _):
                return 'stub_data'
        def gt(_):
            return JinjaTemplate()
        resume = Resume(test_path, stub_reader)
        resume.jinja_env = mocker.Mock()
        resume.jinja_env.get_template = \
            mocker.Mock(return_value=JinjaTemplate())
        resume.to_html()
        assert resume.jinja_env.get_template.called
