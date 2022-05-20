import time
import logging
from Config import Config
from pyrogram import Client, filters
from sql_helpers import forceSubscribe_sql as sql
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(lambda _, __, query: query.data == "onUnMuteRequest")
@Client.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
  user_id = cb.from_user.id
  chat_id = cb.message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    channel = chat_db.channel
    chat_member = client.get_chat_member(chat_id, user_id)
    if chat_member.restricted_by:
      if chat_member.restricted_by.id == (client.get_me()).id:
          try:
            client.get_chat_member(channel, user_id)
            client.unban_chat_member(chat_id, user_id)
            if cb.message.reply_to_message.from_user.id == user_id:
              cb.message.delete()
          except UserNotParticipant:
            client.answer_callback_query(cb.id, text="❗ Присоединитесь нанаш канал и снова нажмите кнопку 'Я подписался(ась) 👍'.", show_alert=True)
      else:
        client.answer_callback_query(cb.id, text="❗ Вы забанины администраторами по другим причинам.", show_alert=True)
    else:
      if not client.get_chat_member(chat_id, (client.get_me()).id).status == 'administrator':
        client.send_message(chat_id, f"❗ **{cb.from_user.mention} пытается разблокировать себя, но я не могу помочь ему, потому что не являюсь администратором в этом чате, выдайте мне права блокировки.**\n__#Покидаю этот чат...__")
        client.leave_chat(chat_id)
      else:
        client.answer_callback_query(cb.id, text="⚠️ Не нажимайте на эту кнопку, если вы можете писать свободно.", show_alert=True)



@Client.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
  chat_id = message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    user_id = message.from_user.id
    if not client.get_chat_member(chat_id, user_id).status in ("administrator", "creator") and not user_id in Config.SUDO_USERS:
      channel = chat_db.channel
      try:
        client.get_chat_member(channel, user_id)
      except UserNotParticipant:
        try:
          buttons = [[
              InlineKeyboardButton('✅ Подписаться на канал', url=f"https://t.me/{channel}")
          ],[
              InlineKeyboardButton('Я подписался(ась) 👍', callback_data='onUnMuteRequest')
          ]]
          reply_markup = InlineKeyboardMarkup(buttons)
          sent_message = message.reply_text(
              "❌ {}, у вас отсутствует подписка на наш канал. Пожалуйста, подпишитесь для возможности общаться тут и после **нажмите кнопку ниже**, чтобы снять ограничения. Сердечное наше спасибо 😊 за подписку!".format(message.from_user.mention),
              disable_web_page_preview=True,
              reply_markup=reply_markup
          )
          client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        except ChatAdminRequired:
          sent_message.edit("❗ **Не достаточно прав.**\n\n__Сделайте меня администратором с правом на блокировку пользователей и повторите попытку снова.\n\n#Покидаю чат...__")
          client.leave_chat(chat_id)
      except ChatAdminRequired:
        client.send_message(chat_id, text=f"❗ **Я не являюсь администратором канала @{channel}**\n\n__Сделайте меня администратором чтобы я мог видить подписчиков канал и повторите попытку снова.\n\n#Покидаю этот чат...__")
        client.leave_chat(chat_id)


@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status is "creator" or user.user.id in Config.SUDO_USERS:
    chat_id = message.chat.id
    if len(message.command) > 1:
      input_str = message.command[1]
      input_str = input_str.replace("@", "")
      if input_str.lower() in ("off", "no", "disable"):
        sql.disapprove(chat_id)
        message.reply_text("❌ **Принудительная подписка отключена успешно.**")
      elif input_str.lower() in ('clear'):
        sent_message = message.reply_text('**Снимаю бан со всех пользователей, которые были замьютены мной...**')
        try:
          for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
            if chat_member.restricted_by.id == (client.get_me()).id:
                client.unban_chat_member(chat_id, chat_member.user.id)
                time.sleep(1)
          sent_message.edit('✅ **Разбан всех пользователей прошёл успешно.**')
        except ChatAdminRequired:
          sent_message.edit('❗ **Не достаточно прав**\n__Я не могу снять ограничения с пользователей, потому что я не являюсь администратором в этом чате, сделайте меня администратором с правом на блокировку.__')
      else:
        try:
          client.get_chat_member(input_str, "me")
          sql.add_channel(chat_id, input_str)
          message.reply_text(f"✅ **Принудительная подписка включена**\n\n__Теперь для тек кто не подписан на [канал](https://t.me/{input_str}), буду выдавать мут и просьбу подписаться, только после они смогут снять с себя ограничения через специальную кнопку.__", disable_web_page_preview=True)
        except UserNotParticipant:
          message.reply_text(f"❗ **Не администратор**\n\n__Я не являюсь администратором [канала](https://t.me/{input_str}). Добавьте меня в качестве администратора, чтобы включить принудительную подписку.__", disable_web_page_preview=True)
        except (UsernameNotOccupied, PeerIdInvalid):
          message.reply_text(f"❗ **Неверный юзернейм канала.**")
        except Exception as err:
          message.reply_text(f"❗ **ОШИБКА:** ```{err}```")
    else:
      if sql.fs_settings(chat_id):
        message.reply_text(f"✅ **В этом чате включена функция принудительной подписки.**\n\n__Для [канала](https://t.me/{sql.fs_settings(chat_id).channel})__", disable_web_page_preview=True)
      else:
        message.reply_text("❌ **Принудительная подписка в этом чате отключена.**")
  else:
      message.reply_text("❗ **Не достаточно прав**\n\n__Доступно только основателю группы.__")
