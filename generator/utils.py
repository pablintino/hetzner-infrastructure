import os


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def safe_file_delete(path):
    if path:
        try:
            os.remove(path)
        except OSError:
            pass

def try_parseint(s):
    try:
        return int(s)
    except ValueError:
        return None