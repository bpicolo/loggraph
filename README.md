# loggraph

Loggraph is a command-line utility for creating graph visualizations to help
make sense of log files. It uses Bokeh to generate graphs.

It currently supports one sort of graph: Graphing values over time (by day)
from JSON logs. (That is, a log whose lines are each a valid JSON object).

## Installation (For pip with Python 3.4+)
pip install loggraph

## Usage Examples

`loggraph overtime -g sum[order.price] log.json`


