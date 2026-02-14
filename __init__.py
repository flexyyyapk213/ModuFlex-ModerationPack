from loads import Description, MainDescription, FuncDescription
from pyrogram.client import Client
from loads import Data

__description__ = Description(
    MainDescription("Плагин для модерации чата.Чтобы все функции работали, вы должны быть админом в чате."),
    FuncDescription('ban', 'Банит пользователя закидывая в чс навсегда или на время.Чтобы указать время введите: 1ч. и/или 1м. и/или 1с. (можно комбинировать, но соблюдайте порядок как на примере).Если не указать время, то бан будет навсегда.', prefixes=['.', '!', '/'], parameters=['ответ на сообщение/айди/@юзер', 'время(не обязательно)']),
    FuncDescription('kick', 'Выкидывает пользователя из чата.', prefixes=['.', '!', '/'], parameters=['ответ на сообщение/айди/@юзер']),
    FuncDescription('unban', 'Разбанивает пользователя.', prefixes=['.', '!', '/'], parameters=['ответ на сообщение/айди/@юзер']),
    FuncDescription('mute', 'Накладывает на пользователя мут.Чтобы указать время введите: 1ч. и/или 1м. и/или 1с. (можно комбинировать, но соблюдайте порядок как на примере).Если не указать время, то мут будет навсегда.', prefixes=['.', '!', '/'], parameters=['ответ на сообщение/айди/@юзер', 'время(не обязательно)']),
    FuncDescription('unmute', 'Снимает с пользователя мут.', prefixes=['.', '!', '/'], parameters=['ответ на сообщение/айди/@юзер']),
    FuncDescription('addword', parameters=('слово',)),
    FuncDescription('rmword', parameters=('слово',))
)

import plugins.ModerationPack.main

def initialization(app: Client):
    config = Data.get_config('ModerationPack')
    config.setdefault({'groups': [], 'censored_words': [], 'punishments': {}})