import argparse
import os
import os.path as osp
import csv
from collections import defaultdict

from .config import cfg

def get_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description="Merge result files.")

    parser.add_argument('config', type=str, help='Path to the config file.')
    parser.add_argument('--output-file', type=str, default=None, help='Path where to save the resulting CSV file. If not provided, will be stored to `<OUTPUT_DIR>/results.csv`')
    parser.add_argument('--csv-base', type=str, default=None, help='Optional starting CSV file. Will be merged with the rest of the results.')

    return parser

def main(args):
    cfg.merge_from_file(args.config)
    cfg.freeze()

    print(cfg)

    # Read base CSV
    entries = defaultdict(dict)
    if args.csv_base is not None:
        with open(args.csv_base, 'r') as csv_base_file:
            reader = csv.reader(csv_base_file, delimiter='\t')
            it = iter(reader)
            next(it) # Skip header
            for row in it:
                entries[row[0]] = {
                    "base": "\n".join(row[1:]),
                    "grade": row[1],
                }

    # Read all results
    all_results = sorted(f for f in os.listdir(cfg.OUTPUT_DIR) if f.endswith('.txt'))
    for res in all_results:
        basename=osp.splitext(res)[0]

        if basename.endswith('_gpt'):
            title = "\n---- GPT Report ----\n"
            field = 'gpt'
        else:
            title = "\n---- Unit Tests ----\n"
            field = 'junit'

        with open(osp.join(cfg.OUTPUT_DIR, res), 'r') as report_file:
            content = title + report_file.read()

        email = basename.split('=')[1]
        entries[email][field] = content

    # Save to CSV
    output_file = args.output_file if args.output_file is not None else osp.join(cfg.OUTPUT_DIR, 'results.csv')
    with open(output_file, 'w') as results_file:
        results_file.write("Email\tOcena\tKomentar\n")
        for email, data in entries.items():
            junit = data.get('junit', '')
            gpt = data.get('gpt', '')
            base = data.get('base', '')
            grade = data.get('grade', '-1')
            comment = "\n\n".join([base, junit, gpt]).replace('\n', '<br>')
            results_file.write(f"{email}\t{grade}\t{comment}\n")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
