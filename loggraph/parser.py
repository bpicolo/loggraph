import ujson as json


def load_json(filepath):
    return (
        json.loads(line)
        for line in open(filepath, 'r')
    )


def log_record_generator(filepath):
    try:
        ext = filepath.split('.')[-1]
    except IndexError:
        raise ValueError('Could not determine extension of {}'.format(filepath))

    try:
        return EXTENSION_TO_loader[ext](filepath)
    except FileNotFoundError:
        raise ValueError('File: {} not found'.format(filepath))


EXTENSION_TO_loader = {
    'json': load_json,
}
