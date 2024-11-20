import os
import pandas as pd


class PriceMachine:

    def __init__(self):
        self.data = []  # список, в котором будут хранится информация о продукте

    def load_prices(self, file_path=''):
        if not file_path:
            file_path = os.getcwd()  # если при вызове метода явно не указывается директория, то используетс ятекущая

        for filename in os.listdir(file_path):  # проходимся по всем файлом (os.listdir(file_path) - все файлы)
            if "price" in filename and filename.endswith('.csv'):  # фильтруем и получаем только тот, который нужен
                file_way = os.path.join(file_path,
                                        filename)  # создает полный путь к файлу, объединив имя каталога и имя файла
                df = pd.read_csv(file_way, delimiter=',')  # загружаем данные в DataFrame  помощью read_csv.
                # Показываем что данные в файле разделены запятыми

                product_col = self._search_product_price_weight(df.columns)  # Определяем нужные столбцы
                if product_col is None:  # проверяем были ли найдены столбцы
                    print(f"Не удалось найти нужные столбцы в файле {filename}.")
                    continue
                # передаем соответствующие данные из product_col
                product_name = df[product_col['product']].astype(str)  # получаем названия продуктов.
                # Здесь мы используем индекс, полученный из product_col['product'], чтобы получить соответствующий
                # столбец из DataFrame - df. Т.к. product_col['product'] равно 0 (что означает, что столбец "товар" это
                # первый столбец), то df[product_col['product']], вернется название всех товаров.
                price = df[product_col['price']].astype(float)  # получаем цены
                weight = df[product_col['weight']].astype(float)  # получаем вес

                for i in range(len(df)):  # проходим по каждому элементу df
                    if weight[i] != 0:  # защищаемся от деления на ноль
                        price_per_kg = price[i] / weight[i]  # рассчитываем цену за кг
                        self.data.append({
                            'name': product_name[i],
                            'price': price[i],
                            'weight': weight[i],
                            'file': filename,
                            'price_per_kg': price_per_kg
                        })  # добавляем информацию в словарь по каждому продукту

    def _search_product_price_weight(self, headers):
        # названия столбцов, котрые мы можем встретить
        product_headers = ['товар', 'название', 'наименование', 'продукт']
        price_headers = ['цена', 'розница']
        weight_headers = ['вес', 'масса', 'фасовка']

        normalized_headers = [header.strip().lower() for header in
                              headers]  # удаляем пробелы и переводим в нижний регистр

        # поиск соответствующих названий столбцов
        product_col = next((h for h in normalized_headers if h in product_headers),
                           None)  # получаем варианты названия столбцов с продуктом
        price_col = next((h for h in normalized_headers if h in price_headers),
                         None)  # получаем варианты названия столбцов с ценой
        weight_col = next((h for h in normalized_headers if h in weight_headers),
                          None)  # получаем варианты названия столбцов с весом

        if product_col and price_col and weight_col:  # возвращаем в функцию load_prices найденные колонки
            return {
                'product': product_col,
                'price': price_col,
                'weight': weight_col
            }

        return None

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                table, th, td {
                    border: 1px solid black;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>

        '''
        for i, row in enumerate(self.data,
                                start=1):  # перебираем элементы списка self.data. row - словарь с данными о продукте
            # i - индекс. enumerate - функция для получения индекса.
            # вставляем данные в html файл
            result += f''' 
                        <tr>
                            <td>{i}</td>
                            <td>{row['name']}</td>
                            <td>{row['price']}</td>
                            <td>{row['weight']}</td>
                            <td>{row['file']}</td>
                            <td>{row['price_per_kg']:.2f}</td>
                        </tr>
                        '''
            # закрываем теги
            result += '''
                        </table>
                    </body>
                    </html>
                    '''

            with open(fname, 'w', encoding='utf-8') as f:  # открываем файл (автоматически закроется)
                f.write(result)  # записываем данные

    def find_text(self, text):
        filtered_data = [item for item in self.data if text.lower() in item['name'].lower()]  # по фрагменту текста
        # находится товар из списка self.data (словарь)
        return filtered_data


# реализация программы
if __name__ == "__main__":
    pm = PriceMachine()  # создаем экземпляр класса
    pm.load_prices()  # явно указываем директорию и просматриваем файлы
    print('Загрузка окончена')

    while True:
        user_input = input(
            "Введите текст для поиска (или 'exit' для выхода): ").strip().lower()  # просим ввести слово для поиска
        if user_input == 'exit':  # стоп слово
            print("Работа завершена.")
            break

        results = pm.find_text(
            user_input)  # вызываем метод find_text, который ищет все товары в self.data, названия которых содержатся в запросе
        results.sort(key=lambda x: x['price_per_kg'])  # сортируем results по цене за кг

        if results:  # если что-то было найдено, то выводятся заголовки, а затем перечень найденных товарос
            print(f"{'№':<3} {'Наименование':<35} {'Цена':<10} {'Вес':<10} {'Файл':<15} {'Цена за кг.':<15}")
            for i, item in enumerate(results, start=1):
                print(
                    f"{i:<3} {item['name']:<35} {item['price']:<10} {item['weight']:<10} {item['file']:<15} {item['price_per_kg']:<15.2f}"
                )
        else:  # если ничего не найдено
            print("По вашему запросу ничего не найдено.")

    pm.export_to_html()  # выгружает все данные в html файл
