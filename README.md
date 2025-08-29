# Программа преобразования Altium Designer bom в перечень элементов и спецификацию по ГОСТ

![Title image](img/img.jpg)

## Использование
1. [Скачайте](https://github.com/murkkot/gost-bom-from-excel/releases) архив с исполняемым файлом. Распайкуте его.
2. Подготовьте входящую спецификацию:
   - Создайте файл OutputJob в Altium Designer.
   - В файле OutputJob нажмите *Add New Report Output -> Bill of Material*.
   - Нажмите на появившуюся строку правой кнопкой мыши и выберите Configure.
   - В поле Properties на вкладке General в строке Template укажите файл шаблона [templates/altium_template.xlsx](templates/altium_template.xlsx).
   - В поле Properties на вкладкe Columns выберите столбцы **Designator, Name, Quantity, Decimal Number**. *Не сортируйте ни один столбец!* Нажмите Ok.
   - Создайте и настройте Output Container. Сгенерируйте файл входящей спецификации. Положите файл в папку *input* внутри папки с программой. Пример входящей спецификаци можно посмотреть в [examples/bom_from_altium.xlsx](examples/bom_from_altium.xlsx).
3. Подготовьте файл документации для спецификации. Пример можно посмотреть в [examples/docs_for_specification.xlsx](examples/docs_for_specification.xlsx). Возьмите пример за основу для создания вашего файла. Положите файл в папку *input* внутри папки с программой.
4. Скачайте исполняемый файл  Запустите программу и следуйте её инструкциям (см. [Запуск программы из исходных кодов](#Запуск-программы-из-исходных-кодов)).
5. Исходящие файлы программа сохраняет в папку папку *output*.


## Запуск программы из исходных кодов
1. Скачайте архив с исходными кодами. В командной строке выполните
```
cd /d "С:/path/to/folder"
git clone https://github.com/murkkot/gost-bom-from-excel.git
```
2. Распакуйте архив.
3. Перейдите в папку с программой
```
cd "gost-bom-from-excel"
```
4. Проверьте, установлен ли python. В коммандной строке выполните
```
python --version
```
5. Если python не установлен, установите его по ссылке: [www.python.org/downloads](https://www.python.org/downloads/).
6. Выполните
```
pip install -r requirements.txt
```
7. Запустите программу
```
cls; python .\main.py
```
8. Следуйте указаниям программы.