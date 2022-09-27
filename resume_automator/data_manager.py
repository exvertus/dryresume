import jsonpatch
import json
from pathlib import Path
from copy import deepcopy

resume_cache = {}

class ResumeData:
    def __init__(self, config_path, use_cache=True):
        config_file = Path(config_path).absolute()
        name = str(config_file)
        cached = resume_cache.get(name, None)
        if use_cache and cached:
            return cached

        self.config_file = config_file
        self.name = name
        self.use_cache = use_cache
        self.data = {}
        self.parent = None
        self.patches = []
        self.reserved_keyword_map = [
            ['parent-data', self._inherit_from_parent],
            ['patches', self._apply_patches]
        ]
        self._load_config(self.config_file)

    def _load_config(self, config_path):
        with config_path.open() as f:
            self.raw_data = json.load(f)
        for field, funct in self.reserved_keyword_map:
            value = self.raw_data.get(field)
            del self.raw_data[field]
            funct(value)
        if not self.parent and not self.patches:
            self.data = self.raw_data.deepcopy()

    def _inherit_from_parent(self, parent_config):
        self.parent_obj = ResumeData(parent_config)
        self.data = self.parent_obj.data.deepcopy()

    def _apply_patches(self, patch):
        self.patch = jsonpatch.JsonPatch(patch)
        self.data = self.patch.apply(self.data)

    def _save_to_cache(self):
        if self.use_cache:
            resume_cache[self.name] = self

def load_resumes(resume_files):
    resume_datas = {}
    for fp in resume_files:
        resume_datas[fp] = ResumeData()
    return resume_datas
