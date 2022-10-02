from dataclasses import replace
import json
import pytest
import yaml
from pathlib import Path

from resume_automator.data_manager import load_resumes

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

@pytest.fixture(params=('samples/results/json/george_resume.json',
                        'samples/results/json/george_resume_baseball.json',
                        'samples/results/json/george_resume_tv.json'
                       ))
def json_result_path(request):
    return Path(__file__).parent.parent / request.param

@pytest.fixture(params=('samples/results/yaml/george_resume.yaml',
                        'samples/results/yaml/george_resume_baseball.yaml',
                        'samples/results/yaml/george_resume_tv.yaml'
                       ))
def yaml_result_path(request):
    return Path(__file__).parent.parent / request.param

class TestIntegrationBroad:
    """No test doubles---full integration.
    """
    @pytest.fixture(scope='class')
    def data_from_json(self):
        resume_files = (
            'samples/input/json/george_resume.json',
            'samples/input/json/george_resume_baseball.json',
            'samples/input/json/george_resume_tv.json'
        )
        resume_files = [Path(__file__).parent.parent / f for f in resume_files]
        return load_resumes(resume_files)

    def test_from_json(self, data_from_json, json_result_path):
        with json_result_path.open() as f:
            result_obj = json.load(f)
        test_key = folder_replace(json_result_path, 'results', 'input')
        assert result_obj == data_from_json[test_key].data

    @pytest.fixture(scope='class')
    def data_from_yaml(self):
        resume_files = (
            'samples/input/yaml/george_resume.yaml',
            'samples/input/yaml/george_resume_baseball.yaml',
            'samples/input/yaml/george_resume_tv.yaml'
        )
        resume_files = [Path(__file__).parent.parent / f for f in resume_files]
        return load_resumes(
            resume_files, reader=lambda x : yaml.load(x, Loader = yaml.Loader))

    def test_from_yaml(self, data_from_yaml, yaml_result_path):
        with yaml_result_path.open() as f:
            result_obj = yaml.load(f, Loader = yaml.Loader)
        test_key = folder_replace(yaml_result_path, 'results', 'input')
        assert result_obj == data_from_yaml[test_key].data
