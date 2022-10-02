import jsonpatch
import json
from pathlib import Path
from copy import deepcopy

resume_cache = {}

class ResumeData:
    def __init__(self, config_path, reader, use_cache=True):
        self.config_file = self.get_config_file(config_path)
        self.use_cache = use_cache
        self.data = {}
        self.parent_obj = None
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
                self.parent_obj = ResumeData(parent_config, self.reader)
        bulk_patch = jsonpatch.JsonPatch(patches)
        self._save(bulk_patch.apply(self.parent_obj.data))

    def _save(self, data):
        global resume_cache
        self.data = deepcopy(data)
        if self.use_cache and not resume_cache.get(str(self.config_file)):
            resume_cache[str(self.config_file)] = self

def load_resumes(resume_files, reader=json.load):
    resume_datas = {}
    for fp in resume_files:
        resume_datas[fp] = ResumeData(fp, reader)
    return resume_datas
