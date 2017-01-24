import numbers
from collections import defaultdict
from datetime import datetime
from functools import reduce

import ciso8601
from dateutil.parser import parse


__const_dict = {}


def gett(record, path):
    return record[path] if path in record else __const_dict


def find_key(record, path):
    return reduce(gett, path, record)


def is_number(value):
    return isinstance(value, numbers.Number)


def is_numeric_string(value):
    try:
        float(value)
    except ValueError:
        return False

    return True


def is_ciso8601_parseable(value):
    return ciso8601.parse_datetime(value) is not None


def parse_from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)


class NumericAccumulator:

    _name = None

    def __init__(self, path):
        self.path = path
        self.values = defaultdict(lambda: 0)

    def result(self, key):
        raise NotImplementedError('Subclass must implement result function')

    def process(self, key, record):
        try:
            value = find_key(record, self.path)
        except TypeError:
            raise ValueError('A record contained a non-number value for {}'.format(self.path))

        self._process(key, value)

    def name(self):
        return '{}({})'.format(self._name, '.'.join(self.path))


# I'm not totally pleased with the level of abstraction of accumulators.
# They have subtle differences, and need to work into the ByDayAccumulator sanely.

# Am somewhat curious what a more functional strategy looks like, but these
# do need to maintain some semblance of state. They're essentially reducers
# on dicts though.
class SumAccumulator(NumericAccumulator):

    _name = 'sum'

    def _process(self, key, value):
        self.values[key] += value

    def result(self, key):
        return self.values[key]


class MaxAccumulator(NumericAccumulator):

    _name = 'max'

    def _process(self, key, value):
        if value > self.values[key]:
            self.values[key] = value

    def result(self, key):
        return self.values[key]


class MinAccumulator(NumericAccumulator):

    _name = 'min'

    def _process(self, key, value):
        if value < self.values[key]:
            self.values[key] = value

    def result(self, key):
        return self.values[key]


class MeanAccumulator(NumericAccumulator):

    _name = 'mean'

    def __init__(self, path):
        super(MeanAccumulator, self).__init__(path)
        self.key_counts = defaultdict(lambda: 0)

    def _process(self, key, value):
        self.values[key] += value
        self.key_counts[key] += 1

    def result(self, key):
        return self.values[key] / self.key_counts[key]


class ByDayAccumulator:

    def __init__(self, accumulators, time_column_name):
        self.dates = set()
        self.accumulators = accumulators
        self.date_getter = None
        self.time_column_name = time_column_name

    def extract_likely_date_column(self, data):
        if self.time_column_name:
            return self.time_column_name

        best_guess = None
        for key in data.keys():
            if key.startswith('timestamp'):
                return key
            if key.startswith('datetime'):
                return key
            if key == 'date':
                return key
            if key.endswith('_time') or key.endswith('_at'):
                best_guess = key

        if not best_guess:
            raise ValueError('Couldn\'t identify a time column. Try specifying --timecolumn')

        return best_guess

    def deduce_time_field(self, record):
        self.time_column_name = self.extract_likely_date_column(record)
        if is_number(record[self.time_column_name]):
            self.date_getter = parse_from_timestamp
        elif is_numeric_string(record[self.time_column_name]):
            self.date_getter = lambda v: parse_from_timestamp(float(v))
        elif is_ciso8601_parseable(record[self.time_column_name]):
            self.date_getter = ciso8601.parse_datetime
        else:
            # Date parsing is a huge bottleneck in parsing these log files.
            # Unfortunately, dateutil taking a guess is drastically slower than
            # anything else, and does not scale to large logs.
            # iso8601 datetimes, and timestamps, are currently quite quick
            self.date_getter = parse

    def process(self, record):
        if not self.date_getter:
            self.deduce_time_field(record)

        date = self.date_getter(record[self.time_column_name])
        self.dates.add(date)
        for accum in self.accumulators:
            accum.process(date, record)

    def get_rendered_axes(self):
        # TODO: fill in empty dates sanely, Otherwise graphs are misleading
        sorted_dates = sorted(list(self.dates))
        return (
            (
                sorted_dates,
                [accumulator.result(date) for date in sorted_dates],
                accumulator.name()
            )
            for accumulator in self.accumulators
        )


NAME_TO_ACCUMULATOR = {
    'mean': MeanAccumulator,
    'max': MaxAccumulator,
    'sum': SumAccumulator
}
