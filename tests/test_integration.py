from copy import deepcopy
import json
import pytest
import shutil
import yaml
from pathlib import Path

from dryresume.resume import create_resumes

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
yaml_dict = {
    'george_resume.yaml': deepcopy(test_dict['base']),
    'george_resume_baseball.yaml': deepcopy(test_dict['child']),
    'george_resume_tv.yaml': deepcopy(test_dict['grandchild'])
}

@pytest.fixture()
def json_files():
    return [REPO_ROOT / f['readfile'] for f in test_dict.values()]

@pytest.fixture()
def yaml_files(json_files, tmp_path):
    result = []
    for json_path in json_files:
        file_ext_only = f"{json_path.stem}.yaml"
        yaml_dest_path = REPO_ROOT / "build" / f"{json_path.stem}.html"
        yaml_src_path = tmp_path / file_ext_only
        with json_path.open() as json_file:
            config = json.load(json_file)
        options = config['options']
        data = config.get('resume')
        options['output-html'] = str(yaml_dest_path)
        if 'parent-data' in options:
            options['parent-data'] = \
                f"{str(Path(options['parent-data']).stem)}.yaml"
        with yaml_src_path.open('w+') as yaml_file:
            yaml.dump({'options': options, 'resume': data}, yaml_file)
        yaml_dict[file_ext_only]['readfile'] = yaml_src_path
        result.append(yaml_src_path)
    return result

@pytest.fixture()
def load_jsons(json_files):
    return create_resumes(json_files)

@pytest.fixture()
def load_yamls(yaml_files):
    return create_resumes(
        yaml_files, reader=lambda x : yaml.load(x, Loader = yaml.Loader))

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

    @pytest.mark.parametrize("name", yaml_dict)
    def test_html_from_yaml(self, load_yamls, name):
        for value, exp_func in yaml_dict[name]['expected'].items():
            test_key = yaml_dict[name]['readfile']
            with load_yamls[test_key].html_target.open() as f:
                html_string = f.read()
            assert exp_func(html_string, value)
