from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


go = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Поехали!', callback_data='go')]])


verb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Больше не показывать', callback_data='no_keywords')],
                                             [InlineKeyboardButton('Не помню', callback_data='next_keywords')],
                                             ])

admin = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('🔐 Закрыть доступ пользователю', callback_data='block_user')],
                                             [InlineKeyboardButton('🤝 Открыть доступ пользователю ', callback_data='white_user')],
                                             [InlineKeyboardButton('➕ Добавить новый глагол', callback_data='add_word')],
                                             [InlineKeyboardButton('➕ Импортировать список глаголов',
                                                                    callback_data='import_words')],
                                             [InlineKeyboardButton('📖 Показать файл со всеми глаголами',
                                                                    callback_data='get_words')],
                                             [InlineKeyboardButton('❌ Удалить существующий глагол', callback_data='del_word')],
                                             ])
