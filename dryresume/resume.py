import argparse
import datetime
import jsonpatch
import json
import logging
import shutil
import yaml
from pathlib import Path
from copy import deepcopy
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

logging.basicConfig(level=logging.INFO)
resume_cache = {}

def year_and_month(date_str, format='%m/%Y'):
    date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
    return date.strftime(format)

def in_groups_of(iterator, groups):
    results = []
    if groups == 0:
        return results
    total_len = len(iterator)
    chunk_len = total_len // groups
    if total_len % groups:
        chunk_len += 1
    for i in range(groups):
        start_slice = i*chunk_len
        end_slice = min((i+1)*chunk_len, total_len)
        results.append(iterator[start_slice:end_slice])
    return results

class Resume:
    def __init__(self, config_path, reader=json.load, use_cache=True):
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
            logging.error(f"Expected to find config file at {config_file}")
            raise FileNotFoundError
        return config_file

    def load_config(self, config_path):
        with config_path.open() as f:
            config = self.reader(f)
        options = config['options']
        data = config.get('resume', {})
        html_path = options.get('output-html', '')
        if html_path:
            raw = config_path.parent / html_path
            self.html_target = raw.resolve()
        parent_ref = options.get('parent-data')
        patches = options.get('patches', [])
        if parent_ref:
            self._inherit_from_parent(parent_ref, patches)
        else:
            self._save(data)
        logging.debug(f"Resume configuration from {config_path} loaded")

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
                # loader=PackageLoader("dryresume"),
                loader=FileSystemLoader(Path(__file__).parent / 'templates'),
                autoescape=select_autoescape()
            )
            self.jinja_env.filters['year_and_month'] = year_and_month
            self.jinja_env.filters['in_groups_of'] = in_groups_of
            self.jinja_env.filters['enumerate'] = enumerate
        template = self.jinja_env.get_template("resume.html")
        if not self.html_target.parent.exists():
            self.html_target.parent.mkdir()
        with self.html_target.open('w') as f:
            f.write(template.render(self.data))
        logging.debug(f"html file output to {self.html_target}")
        style_dir = Path(self.html_target.parent, 'resumeCSS')
        if not style_dir.exists():
            shutil.copytree(
                Path(__file__).parent / 'templates/resumeCSS', style_dir)
            logging.debug(f"Copied css to {style_dir}")

def create_resumes(resume_files, reader=json.load):
    resume_datas = {}
    for fp in resume_files:
        resume_datas[fp] = Resume(fp, reader=reader)
        resume_datas[fp].to_html()
    logging.info(f"Created {len(resume_datas)} resumes.")
    return resume_datas

def main():
    parser = argparse.ArgumentParser(description='Generate resumes from yaml/json')
    parser.add_argument('--files', nargs='+', dest='files')
    parser.add_argument('--format', dest='format', 
        choices=['yaml', 'json'], default='json')
    args = parser.parse_args()
    reader_dict = {
        'yaml': lambda x : yaml.load(x, Loader = yaml.Loader),
        'json': json.load}
    reader = reader_dict[args.format]
    create_resumes(args.files, reader=reader)

if __name__ == "__main__":
    main()
