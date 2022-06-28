![example workflow](https://github.com/Munkushi/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## API для проекта api_yamdb

**Как запустить проект:**

**Создать и активировать виртуальное окружение:**

```
python3 -m venv env для mac/linux
python -m venv venv windows
source venv/Scripts/activate
```

**Установить зависимости из файла requirements.txt:**

```
pip install -r requirements.txt
```

**Выполнить миграции:**

```
python3 manage.py migrate для mac/linux
python manage.py migrate для windows
```

**Запустить проект:**

```
python3 manage.py runserver для mac/linux
python manage.py runserver для windows
```


**Шаблон env-файла.**

DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres 
POSTGRES_USER=пользователь 
POSTGRES_PASSWORD=пароль 
DB_HOST=db 
DB_PORT=5432

**Как запускать проект?**

```
cd infra/
docker-compose up
```

**Для запуска тестов.**

Прописать команду pytest в папке yamdb_final
