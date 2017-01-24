import itertools

from bokeh import palettes
from bokeh.plotting import figure
from bokeh.charts import show

from loggraph import accumulator
from loggraph.parser import log_record_generator


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
