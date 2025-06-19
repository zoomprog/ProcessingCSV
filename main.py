import argparse
import csv
import sys
from tabulate import tabulate


def output_table_console(rows):
    if rows:
        headers = list(rows[0].keys())
        table_date = [[row[headers] for headers in headers] for row in rows]
        print(tabulate(table_date, headers=headers, tablefmt="grid"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--where')
    args = parser.parse_args()

    with open(args.file, 'r') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)
    output_table_console(rows)

if __name__ == '__main__':
    main()