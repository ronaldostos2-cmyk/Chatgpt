
import joblib
from pathlib import Path
import json
from datetime import datetime

MODELS_DIR = Path('models')
MODELS_DIR.mkdir(exist_ok=True)

class ModelRegistry:
    def __init__(self, models_dir: Path = MODELS_DIR):
        self.dir = models_dir
        self.index_file = self.dir / 'registry.json'
        if not self.index_file.exists():
            self._init_index()
        self._load_index()

    def _init_index(self):
        with open(self.index_file, 'w') as f:
            json.dump({'models': [], 'active': None}, f)

    def _load_index(self):
        with open(self.index_file, 'r') as f:
            self.index = json.load(f)

    def register(self, model_obj, metrics: dict):
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        model_name = f'model_{ts}.joblib'
        model_path = self.dir / model_name
        joblib.dump(model_obj, model_path)
        entry = {'name': model_name, 'path': str(model_path), 'metrics': metrics, 'timestamp': ts}
        self.index['models'].append(entry)
        self.index['active'] = model_name
        self._save_index()
        return entry

    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def get_active(self):
        active = self.index.get('active')
        if not active:
            return None
        path = self.dir / active
        if not path.exists():
            return None
        return joblib.load(path)

    def list_models(self):
        return self.index.get('models', [])
