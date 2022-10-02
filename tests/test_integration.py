import json
import pytest
from pathlib import Path

from resume_automator.data_manager import load_resumes, ResumeData

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

    def test_json_files(self, data_from_json, result_path):
        with result_path.open() as f:
            result_obj = json.load(f)
        test_key = Path(str(result_path).replace('results', 'input'))
        assert result_obj == data_from_json[test_key].data
