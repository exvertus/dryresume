import json
import pytest
from pathlib import Path

from resume_automator.data_manager import load_resumes, ResumeData

# Fixtures that should probably be shared later...
@pytest.fixture()
def data_from_json():
    resume_files = (
        '../samples/input/json/george_resume.json',
        '../samples/input/json/george_resume_baseball.json',
        # ../samples/input/json/george_resume_tv.json'
    )
    return load_resumes(resume_files)

@pytest.fixture(params=('../samples/results/json/george_resume.json',
                        '../samples/results/json/george_resume_baseball.json',
                        # ../samples/input/json/george_resume_tv.json'
                       ))
def result_path(request):
    return request.params

class TestIntegrationBroad:
    """No test doubles and include filesystem---full integration.
    """
    @pytest.mark.parametrize()
    def test_json_files(self, data_from_json, result_path):
        result_obj = json.loads(result_path)
        test_key = result_path.replace('results', input)
        assert result_obj == data_from_json[test_key]
