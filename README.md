# Проект hw05_final
### Описание
Перед Вами Django проект YaTube. Учебный проект Яндекс.Практикум.
Проект ставит перед собой цели создания платформы для публикаций, блога. У пользователей есть возможность:
* публиковать записи, содержащие текстовую и графическую информацию
* управлять записями
* оставлять комментарии к записями
* подписываться на авторов и формировать ленту записей
Также реализовано кеширование, покрытие тестами.

Использовано:
* Python v.3.7.5 (https://docs.python.org/3.7/)
* Django v.2.2.16 (https://docs.djangoproject.com/en/2.2/)
* Pytest v.6.2.4 (https://pypi.org/project/pytest/6.2.4/)
* Pillow v.8.3.1 (https://pillow.readthedocs.io/en/stable/releasenotes/8.3.1.html)

### Установка:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/minigraph/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Обновите PIP, дабы избежать ошибок установки зависимостей:

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Автор:
* Михаил Никитин
* * tlg: @minigraf 
* * e-mail: minigraph@yandex.ru; maikl.nikitin@yahoo.com;
