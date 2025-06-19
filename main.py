import argparse
import csv
from tabulate import tabulate

def aggregate(rows, spec: str):
    column_name, value = spec.split('=', 1)

    if 'avg' in spec:
        total = sum(float(row[column_name]) for row in rows) / len(rows)
    elif 'sum' in spec:
        total = sum(float(row[column_name]) for row in rows)
    elif 'min' in spec:
        total = min(float(row[column_name]) for row in rows)
    elif 'max' in spec:
        total = max(float(row[column_name]) for row in rows)
    else:
        return False

    return tabulate([[total]], headers=[value], tablefmt="grid")



def output_table_console(rows):
    if rows:
        headers = list(rows[0].keys())
        table_date = [[row[headers] for headers in headers] for row in rows]
        print(tabulate(table_date, headers=headers, tablefmt="grid"))

def process_numeric(row_value, value, operator_sign):
    """Обрабатывает числовые значения."""
    try:
        row_number = float(row_value)
        filter_number = float(value.strip("'\""))
        return {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '=': lambda a, b: a == b,
        }[operator_sign](row_number, filter_number)
    except ValueError:
        return False

def process_string(row_value, value, operator_sign):
    """Обрабатывает строковые значения."""
    if operator_sign != '=':
        return False
    row_str = str(row_value).strip().lower()
    filter_str = value.strip("'\"").lower()
    return filter_str in row_str

def filter_table(rows, condition_filter):
    """Фильтрует таблицу на основе условия."""
    if not condition_filter:
        return rows

    condition = ' '.join(condition_filter.split())

    for operator_sign in ['=', '>', '<']:
        if operator_sign in condition:
            column_name, value = condition.split(operator_sign, 1)
            break
    else:
        return rows

    filtered = []
    for row in rows:
        try:
            row_value = row[column_name]
            if isinstance(row_value, (int, float)) or (isinstance(row_value, str) and row_value.replace('.', '', 1).isdigit()):
                condition_met = process_numeric(row_value, value, operator_sign)
            else:
                condition_met = process_string(row_value, value, operator_sign)

            if condition_met:
                filtered.append(row)

        except KeyError:
            continue

    return filtered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--where')
    parser.add_argument('--aggregate')
    args = parser.parse_args()

    with open(args.file, 'r') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)
    if args.aggregate:
        result = aggregate(rows, args.aggregate)
        print(result)

    else:
        filtered_rows = filter_table(rows, args.where)
        output_table_console(filtered_rows)


if __name__ == '__main__':
    main()