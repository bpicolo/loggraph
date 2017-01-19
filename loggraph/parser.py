import csv
import ujson as json


def load_json(filepath):
    return (
        json.loads(line)
        for line in open(filepath, 'r')
    )


def load_csv(filepath):
    return (
        row for row in csv.DictReader(open(filepath))
    )


def load_file_for_dataframe(filepath):
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
    'csv': load_csv
}
