import argparse
import sys

from loggraph.loggraph import generate_graph


def overtime_main():
    parser = argparse.ArgumentParser('Simple graphing for your log data.')
    parser.add_argument(
        '-a', '--aggregate',
        dest='aggregates',
        action='append',
        help='How to aggregate data in your columns. Options: count, mean'
    )
    parser.add_argument(
        '-c', '--column',
        dest='columns',
        action='append',
        help='Field to aggregate over.'
    )
    parser.add_argument(
        '--timecolumn',
        dest='time_column',
        help='time column to graph against'
    )
    parser.add_argument(
        'filepath',
        help='Path to log file'
    )
    args = parser.parse_args(sys.argv[2:])

    if args.columns is None or args.aggregates is None:
        raise ValueError(
            'Must specify columns and aggregate methods. Ex: loggraph overtime -c item.price -a mean purchase_log.json'
        )
    if len(args.columns) != len(args.aggregates):
        raise ValueError(
            'Must have same number of columns and aggregates, got {} and {}'.format(
                args.columns, args.aggregates
            )
        )

    generate_graph(
        args.filepath,
        args.columns,
        args.aggregates,
        args.time_column
    )


graph_type_to_main = {
    'overtime': overtime_main
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simple graphing utility for your data',
        usage='''loggraph <graph type> [<args>]

Available graph types are:
   overtime   Graph aggregations on data over time
''')
    parser.add_argument('graph_type', help='Graph type to plot.')
    args = parser.parse_args(sys.argv[1:2])
    if args.graph_type not in set(graph_type_to_main.keys()):
        parser.print_help()
        print('\nUnrecognized graph type: {}'.format(args.graph_type))
        exit(1)

    try:
        graph_type_to_main[args.graph_type]()
    except Exception as e:
        print('Exception trying to generate graph: \n{}'.format(e))
