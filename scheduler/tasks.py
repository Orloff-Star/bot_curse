import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import get_pending_messages, mark_message_sent, update_welcome_stage, WELCOME_MESSAGES

logger = logging.getLogger(__name__)


async def send_scheduled_welcome(bot: Bot):
    """Отправка запланированных приветственных сообщений"""
    try:
        pending_messages = await get_pending_messages()
        logger.info(f"Найдено сообщений для отправки: {len(pending_messages)}")

        for message in pending_messages:
            message_id, user_id, message_stage, username = message

            if message_stage < len(WELCOME_MESSAGES):
                msg_data = WELCOME_MESSAGES[message_stage]

                # Создаем клавиатуру с кнопкой если есть
                keyboard = None
                if msg_data.get('button_text') and msg_data.get('button_url'):
                    builder = InlineKeyboardBuilder()
                    builder.button(
                        text=msg_data['button_text'],
                        url=msg_data['button_url']
                    )
                    keyboard = builder.as_markup()

                try:
                    # Отправляем сообщение с картинкой или без
                    if msg_data.get('image'):
                        await bot.send_photo(
                            chat_id=user_id,
                            photo=msg_data['image'],
                            caption=msg_data['text'],
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await bot.send_message(
                            chat_id=user_id,
                            text=msg_data['text'],
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )

                    # Отмечаем сообщение как отправленное
                    await mark_message_sent(message_id)
                    await update_welcome_stage(user_id, message_stage)

                    logger.info(f"Отправлено сообщение {message_stage} пользователю {user_id}")

                except Exception as e:
                    logger.error(f"Ошибка отправки пользователю {user_id}: {e}")

    except Exception as e:
        logger.error(f"Ошибка в send_scheduled_welcome: {e}")