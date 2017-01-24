import argparse
import sys

from loggraph.loggraph import generate_graph


def overtime_main():
    parser = argparse.ArgumentParser('Simple graphing for your log data.')
    parser.add_argument(
        '-g', '--graph',
        dest='graph_definitions',
        action='append',
        help='How to aggregate data in your columns. Options: count, mean'
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

    if not args.graph_definitions:
        raise ValueError(
            'Must specify something to graph! '
            'Ex: loggraph overtime -g sum(item.price) purchase_log.json'
        )

    generate_graph(
        args.filepath,
        args.graph_definitions,
        args.time_column
    )


graph_type_to_main = {
    'overtime': overtime_main
}


def main():
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

    # import cProfile, pstats
    # pr = cProfile.Profile()
    # pr.enable()
    graph_type_to_main[args.graph_type]()
    # pr.disable()
    # pr.dump_stats('cprofile.prof')


if __name__ == '__main__':
    exit(main())
