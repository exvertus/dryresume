from dataclasses import replace
import json
import pytest
import yaml
from pathlib import Path

from resume_automator.data_manager import load_resumes, ResumeData

def folder_replace(path, search_for, replace_with, limit=1):
    """Returns path with folder name replaced, starting from deepest folder.
    Use limit arg to only replace that many directories."""
    print('break here')
    parts_list = list(path.parts)
    parts_list.reverse()
    start_at = 0
    for i in range(limit):
        inx = parts_list.index(search_for, start_at)
        parts_list[inx] = replace_with
        start_at = inx + 1
    parts_list.reverse()
    return Path(*parts_list)

# Fixtures that should probably be shared later...
@pytest.fixture(params=('samples/results/json/george_resume.json',
                        'samples/results/json/george_resume_baseball.json',
                        'samples/results/json/george_resume_tv.json'
                       ))
def result_path(request):
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

    def test_from_json(self, data_from_json, result_path):
        with result_path.open() as f:
            result_obj = json.load(f)
        # test_key = Path(str(result_path).replace('results', 'input'))
        test_key = folder_replace(result_path, 'results', 'input')
        assert result_obj == data_from_json[test_key].data

    # @pytest.fixture(scope='class')
    # def data_from_yaml(self):
    #     resume_files = (
    #         'samples/input/yaml/george_resume.json',
    #         'samples/input/yaml/george_resume_baseball.json',
    #         'samples/input/yaml/george_resume_tv.json'
    #     )
    #     resume_files = [Path(__file__).parent.parent / f for f in resume_files]
    #     return load_resumes(resume_files)

    # def test_from_yaml(self, data_from_yaml):
    #     pass
