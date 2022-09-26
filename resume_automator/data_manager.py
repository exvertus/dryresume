import jsonpatch
import json
from pathlib import Path

class ResumeData:
    def __init__(self, config_dir):
        self.config_file = Path(config_dir)
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
            self.data = self.raw_data.copy()

    def _inherit_from_parent(self, parent_config):
        self.parent_obj = ResumeData(parent_config)
        self.data = self.parent_obj.data.copy()

    def _apply_patches(self, patch):
        self.patch = jsonpatch.JsonPatch(patch)
        self.data = self.patch.apply(self.data)

def load_resumes(resume_files):
    for fp in resume_files:
        