import json
import pytest
import shutil
import yaml
from pathlib import Path

from dryresume.resume import create_resumes

def folder_replace(path, search_for, replace_with, limit=1):
    """Returns path with folder name replaced, starting from deepest.
    Use limit arg to only replace that many directories.
    """
    parts_list = list(path.parts)
    parts_list.reverse()
    start_at = 0
    for i in range(limit):
        inx = parts_list.index(search_for, start_at)
        parts_list[inx] = replace_with
        start_at = inx + 1
    parts_list.reverse()
    return Path(*parts_list)

REPO_ROOT = Path(__file__).parent.parent

def is_in(to_search, search_for):
    return search_for in to_search

def is_removed(to_search, search_for):
    return not search_for in to_search

test_dict = {
    'base': {
        'readfile': 'samples/input/json/george_resume.json',
        'expected': {
            'George Costanza': is_in,
            'gcostanza@frankandestelle.net': is_in,
            'Architectural design': is_in
        }
    },
    'child': {
        'readfile': 'samples/input/json/george_resume_baseball.json',
        'expected': {
            'George Costanza': is_in,
            'gcostanza@frankandestelle.net': is_removed,
            'george@georgecostanza.com': is_in,
            'Architectural design': is_removed,
            'Sleeping under desk': is_in
        }
    },
    'grandchild': {
        'readfile': 'samples/input/json/george_resume_tv.json',
        'expected': {
            'George Costanza': is_in,
            'Sleeping under desk': is_removed,
            'Screenwriting': is_in
        }
    }
}

@pytest.fixture()
def json_files():
    return [REPO_ROOT / f['readfile'] for f in test_dict.values()]

# @pytest.fixture()
# def yaml_files(json_files, tmp_path):
#     for jf in json_files:

#     yamls = [tmp_path / f"{jf.stem}.yaml" for jf in json_files]
#     for y in yamls:
#         if not y.exists():

@pytest.fixture()
def load_jsons(json_files):
    return create_resumes(json_files)

# @pytest.fixture()
# def load_yamls(yaml_files):
#     result = []
#     for yf in yaml_files:
#         with jf.open('r') as j:
#             data = json.load(j)

class TestIntegrationBroad:
    """No test doubles---full integration.
    """
    @pytest.fixture(scope='class', autouse=True)
    def wipe_build_dir(self):
        repo_build_dir = Path(__file__).parent / 'build'
        if repo_build_dir.exists():
            shutil.rmtree(repo_build_dir)
    
    @pytest.mark.parametrize("name", test_dict)
    def test_html(self, load_jsons, name):
        for value, exp_func in test_dict[name]['expected'].items():
            test_key = REPO_ROOT / test_dict[name]['readfile']
            with load_jsons[test_key].html_target.open() as f:
                html_string = f.read()
            assert exp_func(html_string, value)

    # @pytest.fixture()
    # def json_result(self, json_result_path):
    #     with json_result_path.open() as f:
    #         result_obj = json.load(f)
    #     return result_obj

    # def test_from_json(self, data_from_json, json_result_path, json_result):
    #     test_key = folder_replace(json_result_path, 'results', 'input')
    #     assert json_result == data_from_json[test_key].data

    # @pytest.fixture(scope='class')
    # def data_from_yaml(self):
    #     resume_files = (
    #         'samples/input/yaml/george_resume.yaml',
    #         'samples/input/yaml/george_resume_baseball.yaml',
    #         'samples/input/yaml/george_resume_tv.yaml'
    #     )
    #     resume_files = [Path(__file__).parent.parent / f for f in resume_files]
    #     return create_resumes(
    #         resume_files, reader=lambda x : yaml.load(x, Loader = yaml.Loader))

    # @pytest.fixture()
    # def yaml_result(self, yaml_result_path):
    #     with yaml_result_path.open() as f:
    #         result_obj = yaml.load(f, Loader = yaml.Loader)
    #     return result_obj

    # def test_from_yaml(self, data_from_yaml, yaml_result_path, yaml_result):
    #     test_key = folder_replace(yaml_result_path, 'results', 'input')
    #     assert yaml_result == data_from_yaml[test_key].data

    # def test_to_html(self, data_from_yaml, yaml_result_path):
    #     test_key = folder_replace(yaml_result_path, 'results', 'input')
    #     with data_from_yaml[test_key].html_target.open() as f:
    #         result = f.read()
    #     assert result.startswith('<!DOCTYPE html') and \
    #         data_from_yaml[test_key].data['contact']['name'] in result and \
    #         data_from_yaml[test_key].data['contact']['email'] in result
