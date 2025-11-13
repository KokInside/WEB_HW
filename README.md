## Инструкция

### Клонирование репозитория
> Клонировать репозиторий:
```
git clone https://github.com/KokInside/WEB_HW.git -b hw_3
```

>Скачать RAW-код
[RAW](https://github.com/KokInside/WEB_HW/archive/refs/heads/hw_3.zip)

### Переход в директорию проекта
```
cd WEB_HW
```

### Создание виртуального окружения
> Windows:
```
python -m venv .venv
```

> Linux/MAC:
```
python3 -m venv .venv
```

### Активация виртуального окружения
> Windows:
```
.venv/Scripts/activate
```

> Git Bash Windows
```
source .venv/Scripts/activate
```

> Linux/MAC:
```
source .venv/bin/activate
```

### Установка необходимых компонентов
>Windows:
```
python -m pip install -r requirements.txt
```

>Linux/MAC:
```
python3 -m pip install -r requirements.txt
```

### Переход в директорию Django приложения
```
cd askme
```

### Выполнение миграций БД
> Windows:
```
python manage.py migrate
```

> Linux/MAC:
```
python3 manage.py migrate
```

### Запуск Django сервера
> Windows:
```
python manage.py runserver
```

> Linux/MAC:
```
python3 manage.py runserver
```

Перейдите по адресу, появившемуся в терминале.
```
http://127.0.0.1:8000/
```

## Опционально
### Наполнение базы данных тестовыми данными
*Можно* заполнить базу данных тестовыми данными:

> Windows:
```
python manage.py fill_db [ratio]
```

> Linux/MAC:
```
python3 manage.py fill_db [ratio]
```

Где `[ratio]` - коэффициент заполнения базы в соотношении:
```
пользователи = ratio
вопросы = ratio * 10
ответы = ratio * 100
тэги = ratio
оценки пользователей = ratio * 200
```

Фактически:
```
пользователи = ratio
вопросы = ratio * 10
ответы = 10 * ratio * (ratio - 1)
тэги = ratio
оценки пользователей (вопросы и ответы) = 10 * ratio^2 * (ratio - 1)
```

Теоретически:
```
пользователи = ratio
вопросы = ratio * 10
ответы = ratio * 100 при ratio > 9
тэги = ratio
оценки пользователей = ratio * 200 при ratio > 4
```

### Выход
Для остановки сервера: `CTRL+C`

Для выхода из виртуального окружения:
```
deactivate
```

## Модель базы данных
![Модель базы данных](<readme_img/База Данных.png>)