import chunk
import datetime
import jsonpatch
import json
import shutil
from pathlib import Path
from copy import deepcopy
from jinja2 import Environment, PackageLoader, select_autoescape

resume_cache = {}

def year_only(date_str, format='%Y'):
    date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    return date.strftime(format)

def in_groups_of(input, groups):
    total_len = len(input)
    chunk_len = total_len // groups
    if total_len % groups:
        chunk_len += 1
    results = []
    for i in range(groups):
        start_slice = i*chunk_len
        end_slice = min((i+1)*chunk_len, total_len)
        results.append(input[start_slice:end_slice])
    return results

class Resume:
    def __init__(self, config_path, reader, use_cache=True):
        self.config_file = self.get_config_file(config_path)
        self.use_cache = use_cache
        self.data = {}
        self.parent_obj = None
        self.html_target = \
            Path(self.config_file.parent, f"{self.config_file.stem}.html")
        self.jinja_env = None
        self.patches = []
        self.reader = reader
        self.load_config(self.config_file)

    def get_config_file(self, config_path):
        config_file = Path(config_path).resolve()
        if not config_file.exists():
            raise FileNotFoundError
        return config_file

    def load_config(self, config_path):
        with config_path.open() as f:
            raw_data = self.reader(f)
        html_path = raw_data.get('output-html', '')
        if html_path:
            del raw_data['output-html']
            raw = config_path.parent / html_path
            self.html_target = raw.resolve()
        parent_ref = raw_data.get('parent-data')
        patches = raw_data.get('patches', [])
        if parent_ref:
            self._inherit_from_parent(parent_ref, patches)
        else:
            self._save(raw_data)

    def _inherit_from_parent(self, parent_ref, patches):
        global resume_cache
        parent_config = self.config_file.parent / parent_ref
        if self.use_cache:
            cached = resume_cache.get(str(self.config_file))
            if cached:
                self.parent_obj = cached
            else:
                self.parent_obj = Resume(parent_config, self.reader)
        bulk_patch = jsonpatch.JsonPatch(patches)
        self._save(bulk_patch.apply(self.parent_obj.data))

    def _save(self, data):
        global resume_cache
        self.data = deepcopy(data)
        if self.use_cache and not resume_cache.get(str(self.config_file)):
            resume_cache[str(self.config_file)] = self

    def to_html(self):
        if not self.jinja_env:
            self.jinja_env = Environment(
                loader=PackageLoader("dryresume"),
                autoescape=select_autoescape()
            )
            self.jinja_env.filters['year_only'] = year_only
            self.jinja_env.filters['in_groups_of'] = in_groups_of
            self.jinja_env.filters['enumerate'] = enumerate
        template = self.jinja_env.get_template("resume.html")
        if not self.html_target.parent.exists():
            self.html_target.parent.mkdir()
        with self.html_target.open('w') as f:
            f.write(template.render(self.data))
        style_dir = Path(self.html_target.parent, 'resumeCSS')
        if not style_dir.exists():
            shutil.copytree(
                Path(__file__).parent / 'templates/resumeCSS', style_dir)
        print('test')

def create_resumes(resume_files, reader=json.load):
    resume_datas = {}
    for fp in resume_files:
        resume_datas[fp] = Resume(fp, reader)
        resume_datas[fp].to_html()
    return resume_datas
