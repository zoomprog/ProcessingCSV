import argparse
import csv
from tabulate import tabulate


def output_table_console(rows):
    if rows:
        headers = list(rows[0].keys())
        table_date = [[row[headers] for headers in headers] for row in rows]
        print(tabulate(table_date, headers=headers, tablefmt="grid"))

def filter_table(rows, condition_filter):
    if not condition_filter:
        return rows

    condition = ' '.join(condition_filter.split())

    for op in ['=', '>', '<']:
        if op in condition:
            left, right = condition.split(op, 1)
            break
    else:
        return rows

    filtered = []
    for row in rows:
        try:
            row_value = row[left]

            is_numeric = True
            try:
                row_val_num = float(row_value)
                right_val_num = float(right.strip("'\""))
            except ValueError:
                is_numeric = False
                row_val_num = str(row_value).strip().lower()
                right_val_num = right.strip("'\"").lower()


            if is_numeric:
                match = {
                    '>': lambda a, b: a > b,
                    '<': lambda a, b: a < b,
                    '=': lambda a, b: a == b,
                }[op](row_val_num, right_val_num)
            else:
                if op == '==':
                    match = row_val_num == right_val_num
                elif op == '=':
                    match = right_val_num in row_val_num
                else:
                    match = False

            if match:
                filtered.append(row)

        except KeyError:
            continue

    return filtered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--where')
    args = parser.parse_args()

    with open(args.file, 'r') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)
    filtered_rows = filter_table(rows, args.where)
    output_table_console(filtered_rows)


if __name__ == '__main__':
    main()