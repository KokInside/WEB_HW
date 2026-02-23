## Инструкция  

### Клонирование репозитория
> Клонировать репозиторий:

```
git clone https://github.com/KokInside/WEB_HW.git -b hw_6
```

>Скачать RAW-код
[RAW](https://github.com/KokInside/WEB_HW/archive/refs/heads/hw_6.zip)

### Переход в директорию проекта

```
cd WEB_HW
```

### Создание виртуального окружения

```
python3 -m venv .venv
```

### Активация виртуального окружения

```
source .venv/bin/activate
```

### Установка необходимых компонентов

```
python3 -m pip install -r requirements.txt
```

### Переход в директорию Django приложения

```
cd askme
```

### Выполнение миграций БД

```
python3 manage.py migrate
```

### Сборка статических файлов

```
python3 manage.py collectstatic
```
`yes`, при необходимости.

### Установка node.js зависимостей

Находясь в `WEB_HW/askme` выполнить:

```
npm install
```

### Настройка прокси-сервера

В конфигурационный файл nginx нужно вставить или скопировать конфиг из `WEB_HW/askme/conf/nginx.local`.

И проверить правильность конфигурации:

```
sudo nginx -t
```

Затем необходимо запустить nginx:

```
sudo nginx
sudo nginx -s reload
```

### Запуск wsgi-сервера

Находясь в `WEB_HW/askme` с активированным `venv` запустить gunicorn:

```
gunicorn -c conf/gunicorn.conf.py
```

На экране должна появиться информация о воркерах.

### Запуск сервера-сообщений

Находясь в `WEB_HW/askme/conf`, выполнить:

```
centrifugo -c centrifugo.config.json
```

### Запуск тестового SMTP-сервера

Запустить maildev:

```
npx maildev
```

Должны вывестись порты, на которых открыт веб-интерфейс и smtp-сервер.

Он доступен по `http://<PROXY-SERVER-NAME>/maildev`

### Настройка кэширования

Для правильной работы кэширования, необходимо установить и запустить redis:

```
sudo apt install redis-server -y
sudo systemctl start redis
```
Он должен запуститься на стандартном порту 6379.

Для проверки работы:
```
sudo systemctl status redis
```

```
redis-cli
```

```
ping
```
Должно ответить `PONG`

### Проект

Проект доступен по хосту и порту из конфига nginx.

## Опционально

### Наполнение базы данных тестовыми данными

*Можно* заполнить базу данных тестовыми данными:

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
ответы = ratio * 100 при ratio > 10
тэги = ratio
оценки пользователей = ratio * 200 при ratio > 4
```

## Модель базы данных

![Модель базы данных](<readme_img/База Данных.png>)


```
пользователи = ratio
вопросы = ratio * 10
ответы = 10 * ratio * (ratio - 1)
тэги = ratio
оценки пользователей (вопросы и ответы) = 10 * ratio^2 * (ratio - 1)
```