# Sferum Bot от [@xKARASb](https://github.com/xKARASb)

This `README` is also available on [English](https://github.com/xKARASb/SferumBot/blob/main/README_EN.md) <- click.

## Как пользоваться?

1. Клонируем репозиторий:

``` sh
git clone https://github.com/xKARASb/SferumBot.git
cd SferumBot
```

2. Созаём и активируем виртуальное окружение:

``` sh
python3 -m venv venv
. venv/bin/activate
```

> **ЗАМЕТКА**
>
> Вторая команда для Windows выглядит следющим образом:
>
> ```
> .\venv\Scripts\Activate
> ```

3. Установка зависимостей:

``` sh
pip install -r requirements.txt
```

4. Заполняем поля в `.env.dist`:

- `AUTH_COOKIE`

[Инструкция для `Microsoft Edge`](https://github.com/xKARASb/SferumBot/issues/9)

Зайдите в [Sferum](https://web.vk.me/).

Нажмите <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd>, после чего откроются параметры для разработчиков.

Перейдите в раздел `Application` (Приложение) >> `Storage` (Хранилище) >> `Cookies` (Файлы cookie) >> `https://web.vk.me`.

Затем введите в поле поиска "remixdsid" и скопируйте его значение (должно начинаться с "vk1.a.").

Заполните поле в `.env.dist`.

- `BOT_TOKEN`

Перейдите в [@BotFather](https://t.me/BotFather).

Введите команду `/newbot`, а затем укажите название и юзернейм для бота (отдельными сообщениями).

Скопируйте токен и вставьте его в `.env.dist`.

- `TG_USER_ID`

Вы можете получить ваш id [в этом боте](https://t.me/username_to_id_bot).

Скопируйте его и вставьте его в `.env.dist`.

- `TG_CHAT_ID`

Можно оставить пустым, если не собираетесь использовать бота в группе/канале.

В настройках телеграм включите отображения id: `Настройки` > `Продвинутые настройки` > `Эксперементальные настройки` > `Show Peer IDs in profile`.

Запи

> **ВАЖНО**
>
> Дайте боту права администратора в группе/канале.

> **ЗАМЕТКА**
>
> Чтобы пересылать сообщения в один из разделов супергруппы вы можете указать его id в `TG_TOPIC_ID`.

- `VK_CHAT_ID`

Получите id чата, открыв его в браузере:

```
https://web.vk.me/convo/{здесь нужный нам id}
```

Вы можете записать чаты, из которых необходимо пересылать сообщения в `.env.dist` следующим образом:

```
VK_CHAT_ID=200000015, 200000016
VK_CHAT_ID=200000015,200000016
VK_CHAT_ID=200000015
```

5. Переименуйте `.env.dist` -> `.env`.

6. Запуск:

``` sh
python3 startup.py
```

## Работает на

- [Python 3.13](https://docs.python.org/3.13/)

## Использованные технологии:

- [Asyncio](https://docs.python.org/3/library/asyncio.html)
- [Aiogram 3.x](https://docs.aiogram.dev/en/latest/)
- [Requests](https://requests.readthedocs.io/en/latest/)

## Возможности:

- Пересылать текстовые сообщения в telegram.
- Пересылать медта в telegram (ограничиваясь лимитами telegram).
- Отправка пересланных сообщений с медиа.
- Можно получать сообщения из нескольких чатов.

## Лицензия:

MIT

**Открытое програмное обеспечение, черт возьми!**
