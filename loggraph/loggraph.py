import itertools

import pandas
from bokeh import palettes
from bokeh.plotting import figure
from bokeh.charts import show

from loggraph import accumulator
from loggraph.parser import log_record_generator


def extract_likely_date_column(data):
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


def get_time_column_name(explicit_time_column, data):
    if not explicit_time_column:
        return extract_likely_date_column(data)

    if explicit_time_column and explicit_time_column not in data:
        raise ValueError('Desired time column {} not found in {}'.format(
            explicit_time_column,
            data.keys().tolist()
        ))

    return explicit_time_column


# This is probably not the optimal strategy for unnesting dataframes but the
# json strategy seems much worse right now, as it would be lots of python-level copying.
# Besides, everybody loves recursion.
def normalize_dataframe(data):
    # No rows in this dataframe, nothing to normalize
    if data.shape[0] == 0:
        return data

    for key in data.select_dtypes(include=[object]):
        if not isinstance(data[key].iloc[data[key].first_valid_index()], dict):
            return data

        new_frame = pandas.DataFrame.from_records(data[key])

        new_frame = new_frame.rename(columns=lambda column_name: '{}.{}'.format(key, column_name))
        data = data.join(normalize_dataframe(new_frame))
        data = data.drop(key, 1)

    return data


def aggregate_data_for_plot(time_column_name, data, column_name, aggregate_type):
    return getattr(
        data.groupby(time_column_name, as_index=False)[column_name],
        aggregate_type
    )()


def accumulators_for_definitions(graph_definitions):
    accumulator_definitions = (
        tuple(definition[:-1].split('['))
        for definition in graph_definitions
    )

    return [
        accumulator.NAME_TO_ACCUMULATOR[name](path.split('.'))
        for name, path in accumulator_definitions
    ]


def generate_graph(
    filepath,
    graph_definitions,
    time_column_name
):
    accumulators = accumulators_for_definitions(graph_definitions)
    record_generator = log_record_generator(filepath)
    by_day = accumulator.ByDayAccumulator(accumulators, time_column_name)
    for record in record_generator:
        by_day.process(record)

    colors = itertools.cycle(palettes.Set2[8])

    plot = figure(width=800, height=400, x_axis_type='datetime')
    plot.xaxis.axis_label = by_day.time_column_name.capitalize()

    for x_axis, y_axis, legend in by_day.get_rendered_axes():
        plot.line(
            x_axis,
            y_axis,
            legend=legend,
            color=next(colors)
        )

    show(plot)
