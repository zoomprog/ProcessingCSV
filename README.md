# Команды
## Вывести таблицу без фильтров

```bash
  python main.py --file products.csv
```
## Отфильтровать строки
```bash
  python main.py --file products.csv --where "brand='apple'"
```
## Выполнить агрегацию
```bash
  python main.py --file products.csv --aggregate "price=avg"
```
## Выполнить агрегацию c фильтрацией строки
```bash
  python main.py --file products.csv --where "brand='xiaomi'" --aggregate "price=min"
```
## Запустить тесты
```bash
  cd test 
  pytest -q
```
