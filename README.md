<details>
<summary>Project stack</summary>

- Python 3.7
- Django 2.1
- Django REST Framework 
- Djoser 
- Pillow
- Docker Compose 
- Gunicorn
- Nginx
- PostgresQL
- GitHub Actions

</details>

### Описание:
Сайт "Foodgram" - это онлайн-сервис и API для него.
На этом сервисе пользователи могут публиковать рецепты, 
подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список избранных или список покупок 
и скачивать список продуктов в виде PDF файла, 
необходимых для приготовления одного или нескольких выбранных блюд.


### Инструкция по запуску:
Клонируйте репозиторий:

Установите и активируйте виртуальное окружение:

- *для MacOS:*
    ```commandline
    python3 -m venv venv
    ```
- *для Windows:*
    ```commandline
    python -m venv venv
    source venv/bin/activate
    source venv/Scripts/activate
    ```
Установите зависимости из файла requirements.txt:
```commandline
pip install -r requirements.txt
```
Примените миграции:
```commandline
python manage.py migrate
```
В папке с файлом manage.py выполните команду для запуска локально:
```commandline
python manage.py runserver
```

### Сборка контейнера:
Перейти в папку *infra/*:
```commandline
cd infra/
```
Разверните контейнеры при помощи docker-compose:
```commandline
docker-compose up -d --build
```
Выполните миграции:
```commandline
docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```commandline
docker-compose exec backend python manage.py createsuperuser
```
Заполните базу данных ингредиентами и тегами выполнив команду:
```commandline
docker-compose exec backend python manage.py from_csv_to_db --no-input
```
Остановка контейнеров:
```commandline
sudo docker-compose stop
```

### Автор проекта:

[Rymanov Rostislav](https://github.com/RostIiIslav)
