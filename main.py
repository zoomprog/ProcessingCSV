import argparse
import csv
from typing import Any, Dict, List, Optional, Union

from tabulate import tabulate


def aggregate(rows: List[Dict[str, Any]], spec: str) -> Union[str, bool]:
    column_name, value = spec.split('=', 1)

    if 'avg' in spec:
        total: float = round(
            sum(float(row[column_name]) for row in rows) / len(rows), 2
        )
    elif 'sum' in spec:
        total = sum(float(row[column_name]) for row in rows)
    elif 'min' in spec:
        total = min(float(row[column_name]) for row in rows)
    elif 'max' in spec:
        total = max(float(row[column_name]) for row in rows)
    else:
        return False

    return tabulate([[total]], headers=[value], tablefmt="grid")


def output_table_console(rows: List[Dict[str, Any]]) -> None:
    if rows:
        headers = list(rows[0].keys())
        table_data = [[row[h] for h in headers] for row in rows]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


def process_numeric(row_value: Union[str, int, float],value: str,operator_sign: str,) -> bool:
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


def process_string(row_value: Any, value: str, operator_sign: str) -> bool:
    """Обрабатывает строковые значения."""
    if operator_sign != '=':
        return False
    row_str = str(row_value).strip().lower()
    filter_str = value.strip("'\"").lower()
    return filter_str in row_str


def filter_table(rows: List[Dict[str, Any]], condition_filter: Optional[str]) -> List[Dict[str, Any]]:
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

    filtered: List[Dict[str, Any]] = []
    for row in rows:
        try:
            row_value = row[column_name]
            if isinstance(row_value, (int, float)) or (
                isinstance(row_value, str) and row_value.replace('.', '', 1).isdigit()
            ):
                condition_met = process_numeric(row_value, value, operator_sign)
            else:
                condition_met = process_string(row_value, value, operator_sign)

            if condition_met:
                filtered.append(row)

        except KeyError:
            continue

    return filtered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--where')
    parser.add_argument('--aggregate')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        rows: List[Dict[str, Any]] = list(csv_reader)

    filtered_rows = filter_table(rows, args.where)

    if args.aggregate:
        if not filtered_rows:
            print('Нет строк, удовлетворяющих условию фильтра.')
            return
        result = aggregate(filtered_rows, args.aggregate)
        print(result)
    else:
        output_table_console(filtered_rows)


if __name__ == '__main__':
    main()