import argparse, sys, re
import csv
from typing import Any, Dict, List, Optional, Union

from tabulate import tabulate

# Добавьте / верните эту строку до создания AGG_RE
AGG_ALLOWED = ('avg', 'sum', 'min', 'max')

# затем идёт выражение с использованием этого списка
AGG_RE = re.compile(rf"^(\w+)=({'|'.join(AGG_ALLOWED)})$")


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

def validate_where(where: str) -> None:
    if not where:
        return
    condition = ' '.join(where.split())
    statement = [operator for operator in ['=', '>', '<'] if operator in condition]
    if len(statement) == 0:
        print('Не введён оператор (=, < или >)')
        sys.exit(2)
    elif len(statement) != 1:
        print('Некорректное количество операторов — должно быть использовано один оператор (=, < или >).')
        sys.exit(2)

    operator = statement[0]
    column, value = condition.split(operator)
    if not column.strip() or not value.strip():
        print("Некорректный формат --where, убедитесь, что слева и справа от оператора указаны значения.")
        sys.exit(2)

def validate_aggregate(spec: str) -> None:
    if not spec:
        return
    if not AGG_RE.match(spec):
        print("Некорректное значение --aggregate. Используйте формат 'column=avg|sum|min|max'")
        sys.exit(2)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, type=argparse.FileType('r', encoding='utf-8'),help='products.csv')
    parser.add_argument('--where')
    parser.add_argument('--aggregate')
    args = parser.parse_args()
    validate_where(args.where)
    validate_aggregate(args.aggregate)

    csv_reader = csv.DictReader(args.file)
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