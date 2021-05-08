def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def try_parseint(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def get_optional_arg(namespace, arg, default=None):
    value = vars(namespace).get(arg, default)
    return value if value else default


def common_start(values):
    if len(values) != 0:
        start = values[0]
        while start:
            if all(value.startswith(start) for value in values):
                return start
            start = start[:-1]
    return ""
