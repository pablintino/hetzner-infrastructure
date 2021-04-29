import os
import shutil
import pathlib


def move_content_to_parent(directory_path, delete_directory=True):
    path = pathlib.Path(directory_path)
    if path == path.parent and delete_directory:
        raise ValueError('cannot move and delete directory cause if fs root')
    for filename in os.listdir(directory_path):
        shutil.move(os.path.join(directory_path, filename), os.path.join(path.parent, filename))

    if delete_directory:
        os.rmdir(directory_path)
