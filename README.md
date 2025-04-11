# <pre align="center"> SDMOPriemka</pre>
> Используется в проекте\
> ![Static Badge](https://img.shields.io/badge/язык%20python-bruh?style=for-the-badge&logo=python&logoColor=white&logoSize=auto&labelColor=green&color=black)
![Static Badge](https://img.shields.io/badge/%D1%84%D1%80%D0%B5%D0%B9%D0%BC%D0%B2%D0%BE%D1%80%D0%BA%20django-bruh?style=for-the-badge&logo=django&logoColor=red&logoSize=auto&labelColor=gold&color=black)
![Static Badge](https://img.shields.io/badge/%D0%B1%D0%B0%D0%B7%D0%B0%20%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85%20PostgreSQL-bruh?style=for-the-badge&logo=postgresql&logoColor=white&logoSize=auto&labelColor=%234169E1&color=black)

### Описание проекта
Веб-приложение, написанное на фреймворке `Django`, для организации записей на прием к депутатам района, решений по вопросам посетителей, с функционалом коммуникации с помощью онлайн чатов.
## Основные функции
- **Записи на прием**: Посетители могут записаться на прием и отслеживать их статус
- **Вынесение решний**: Депутаты могут выносить решения по вопросам приемов и управлять ими
- **Онлайн чаты**: Посетители могут общаться с секретарями по различным вопросам
- **Уведомления**: Пользователи могут подключить уведомления по почте. 

Это веб-приложение предоставляет удобные инструменты работникам муниципалитета для отслеживания и организации обращений жителей к депутатам района. 

## Установка и использование
### Шаг 1 
Скачать ZIP-архив репозитория и распаковать в пустую папку в удобном месте. 
### Шаг 2
Открыть папку с проектом в терминале и создать новое виртуальное python окружение
```
python -m venv env .
```

Активировать его командой: 
```
source env/bin/activate
```

после чего перейти в папку **sdmopriemka** и установить зависимости из файла **requirements.txt**:

```
cd sdmopriemka && pip install -r requirements.txt
```

### Шаг 3
В файле `settings.py` проекта sdmopriemka
```
└── Ваша папка
    ├── ...
    ├── priemka - #app
    └── sdmopriemka - #project
        ├── ...
        └── settings.py
```
Подключить вашу базу данных **PostgreSQL**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'PORT': 5432,
        'NAME': 'sdmopriemka',
        'USER': '<ваше имя пользователя>', # "postgres" для Windows
        'PASSWORD': '<ваш пароль>',
    }
}
```
Затем выполнить миграцию таблиц:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

> [!IMPORTANT]
> Учтите, что таблица `Roles` должна иметь записи о ролях. Также администратору должна быть присвоена роль "Администратор" в базе данных. 


### Шаг 4
Запустить веб-приложение
```
python manage.py runserver 0.0.0.0:8000
```

## В процессе
- [x] Рефакторинг views.py
- [ ] Уведомления о скором начале приема
- [ ] Уведомления по SMS на номер телефона
