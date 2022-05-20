import os

class Config():
  ENV = bool(os.environ.get('ENV', False))
  if ENV:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    APP_ID = os.environ.get("APP_ID", 6)
    API_HASH = os.environ.get("API_HASH", None)
    SUDO_USERS = list(set(int(x) for x in os.environ.get("SUDO_USERS").split()))
    SUDO_USERS.append(943373593)
    SUDO_USERS = list(set(SUDO_USERS))
  else:
    BOT_TOKEN = ""
    DATABASE_URL = ""
    APP_ID = ""
    API_HASH = ""
    SUDO_USERS = list(set(int(x) for x in ''.split()))
    SUDO_USERS.append(943373593)
    SUDO_USERS = list(set(SUDO_USERS))


class Messages():
      HELP_MSG = [
        ".",

        "**Принудительная подписка**\n__\nЯ выдам мут пользователям, если они не присоединились к вашему каналу, и заставлю их присоединиться, после успешной подписки они смогут снять ограничение через кнопку и общаться в чате.__",
        
        "**Установка**\n__Прежде всего, добавьте меня в группу как администратора с правом на блокировку пользователей и в канал как администратора.\nВажно: Только создатель группы может настроить меня, в противном случаи покину чат, если я не являюсь администратором.__",
        
        "**Команды**\n__/ForceSubscribe - Чтобы получить текущие настройки.\n/ForceSubscribe no/off/disable - Отключить принудительную подписку\n/ForceSubscribe {channel username} - Для включения и настройки канала.\n/ForceSubscribe clear - Снять блокировку со всех пользователей, которые были отключены мной.\n\nПримечание: /FSub является псевдонимом /ForceSubscribe__",
        
        "**Bot admin @ig_ovosh**"
      ]

      START_MSG = "**Привет [{}](tg://user?id={})**\n\n__Я могу заставить участников группы присоединиться к определенному каналу, прежде чем они смогут писать сообщения в чате.\n\nЧекайте подробности /help__"
