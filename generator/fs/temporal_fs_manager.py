import os
import uuid
import tempfile


class TemporalFsManager:

    def __init__(self):
        self.temp_paths = {}

    def get_temporal_directory(self, dir_id=None):
        dir_id = dir_id if dir_id else uuid.uuid4().hex
        if dir_id not in self.temp_paths:
            self.temp_paths[dir_id] = tempfile.TemporaryDirectory()
        return self.temp_paths.get(dir_id).name

    def get_temporal_file(self, file_id=None):
        file_id = file_id if file_id else uuid.uuid4().hex
        if file_id not in self.temp_paths:
            self.temp_paths[file_id] = tempfile.NamedTemporaryFile(delete=False).name
        return self.temp_paths.get(file_id)

    def cleanup(self):
        for path in self.temp_paths.values():
            if isinstance(path, tempfile.TemporaryDirectory):
                path.cleanup()
            else:
                os.remove(path)
