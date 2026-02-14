import traceback
from loads import func, Data
from pyrogram.client import Client
from pyrogram import filters
from pyrogram import types
from pyrogram.utils import zero_datetime
from pyrogram import enums
import re
from datetime import datetime, timedelta
from pyrogram.errors import exceptions

config = Data.get_config(__file__)

async def filter_chats_id(_, __, message: types.Message) -> bool:
    return bool(str(message.chat.id) in config['groups'])

chat_id_in_reg = filters.create(filter_chats_id, 'ChatIdInReg')

@func(filters.command('ban', prefixes=['.', '!', '/']) & filters.me)
async def ban_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')

    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.mention
    else:
        try:
            user_identifier_str = message.text.split(' ')[1]
        except IndexError:
            return await message.edit_text('Вы не указали параметры: {ответ на сообщение/айди/@юзер} {время(не обязательно)}')

        if user_identifier_str.isnumeric():
            target_user_id = int(user_identifier_str)
        else:
            if '@' in user_identifier_str:
                user_identifier_str = user_identifier_str.replace('@', '')
            
            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            target_user_id = chat_member.user.id
            user_first_name = chat_member.user.mention
    
    if not message.reply_to_message:
        duration_input_str = ' '.join(message.text.split(' ')[2:])
    else:
        duration_input_str = ' '.join(message.text.split(' ')[1:])

    total_ban_seconds: int = 0
    
    if duration_input_str:
        duration_matches_raw = re.findall(r'(\d*ч\.) (\d*м\.) (\d*с\.)|(\d*ч\.) (\d*с\.)|(\d*ч\.) (\d*м\.)|(\d*м\.) (\d*с\.)|(\d*ч\.)|(\d*м\.)|(\d*с\.)', duration_input_str)

        if not duration_matches_raw:
            return await message.edit_text('Вы не верно указали параметры: {время(не обязательно)}.Подробнее в `.help ModerationPack`')

        active_duration_parts = [part for part in duration_matches_raw[0] if part]

        for part_str in active_duration_parts:
            value = int(re.match(r'\d+', part_str).group(0))
            
            if 'ч.' in part_str:
                total_ban_seconds += value * 3600
            elif 'м.' in part_str:
                total_ban_seconds += value * 60
            elif 'с.' in part_str:
                total_ban_seconds += value
    
    ban_expiry_datetime = datetime.now() + timedelta(seconds=total_ban_seconds) if total_ban_seconds != 0 else zero_datetime()
    
    try:
        await app.ban_chat_member(message.chat.id, target_user_id, ban_expiry_datetime)
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')
    
    if total_ban_seconds == 0 or total_ban_seconds > 31622400 or total_ban_seconds < 30:
        await message.edit_text(f'Вы забанили пользователя {user_first_name} на: **навсегда**.')
    else:
        _hours = total_ban_seconds // 3600
        _minutes = (total_ban_seconds % 3600) // 60
        _seconds = total_ban_seconds % 60

        _text = ""

        if int(_hours) > 0:
            _text += f"{_hours}ч. "
        
        if int(_minutes) > 0:
            _text += f"{_minutes}м. "
        
        if _seconds > 0:
            _text += f"{_seconds}с."

        await message.edit_text(f'Вы забанили пользователя {user_first_name} на: **{_text}**')

@func(filters.command('kick', ['.', '!', '/']) & filters.me)
async def kick_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.mention
    else:
        try:
            user_identifier_str = message.text.split(' ')[1]
        except IndexError:
            return await message.edit_text('Вы не указали параметры: {ответ на сообщение/айди/@юзер} {время(не обязательно)}')

        if user_identifier_str.isnumeric():
            target_user_id = int(user_identifier_str)

            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            user_first_name = chat_member.user.mention
        else:
            if '@' in user_identifier_str:
                user_identifier_str = user_identifier_str.replace('@', '')
            
            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            target_user_id = chat_member.user.id
            user_first_name = chat_member.user.mention
    
    try:
        await app.ban_chat_member(message.chat.id, target_user_id)
        await app.unban_chat_member(message.chat.id, target_user_id)
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')
    
    await message.edit_text(f'Вы успешно выкинули пользователя {user_first_name} из чата.')

@func(filters.command('unban', ['.', '!', '/']) & filters.me)
async def unban_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.mention
    else:
        try:
            user_identifier_str = message.text.split(' ')[1]
        except IndexError:
            return await message.edit_text('Вы не указали параметры: {ответ на сообщение/айди/@юзер} {время(не обязательно)}')

        if user_identifier_str.isnumeric():
            target_user_id = int(user_identifier_str)

            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            user_first_name = chat_member.user.mention
        else:
            if '@' in user_identifier_str:
                user_identifier_str = user_identifier_str.replace('@', '')
            
            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            target_user_id = chat_member.user.id
            user_first_name = chat_member.user.mention
    
    try:
        await app.unban_chat_member(message.chat.id, target_user_id)
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')
    
    await message.edit_text(f'Вы сняли бан с пользователя {user_first_name}')

@func(filters.command('mute', ['.', '!', '/']) & filters.me)
async def mute_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.mention
    else:
        try:
            user_identifier_str = message.text.split(' ')[1]
        except IndexError:
            return await message.edit_text('Вы не указали параметры: {ответ на сообщение/айди/@юзер} {время(не обязательно)}')

        if user_identifier_str.isnumeric():
            target_user_id = int(user_identifier_str)
        else:
            if '@' in user_identifier_str:
                user_identifier_str = user_identifier_str.replace('@', '')
            
            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            target_user_id = chat_member.user.id
            user_first_name = chat_member.user.mention
    
    if not message.reply_to_message:
        duration_input_str = ' '.join(message.text.split(' ')[2:])
    else:
        duration_input_str = ' '.join(message.text.split(' ')[1:])

    total_mute_seconds: int = 0
    
    if duration_input_str.isnumeric():
        target_user_id = int(user_identifier_str)

        chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
        user_first_name = chat_member.user.mention
    elif duration_input_str:
        duration_matches_raw = re.findall(r'(\d*ч\.) (\d*м\.) (\d*с\.)|(\d*ч\.) (\d*с\.)|(\d*ч\.) (\d*м\.)|(\d*м\.) (\d*с\.)|(\d*ч\.)|(\d*м\.)|(\d*с\.)', duration_input_str)

        if not duration_matches_raw:
            return await message.edit_text('Вы не верно указали параметры: {время(не обязательно)}.Подробнее в `.help ModerationPack`')

        active_duration_parts = [part for part in duration_matches_raw[0] if part]

        for part_str in active_duration_parts:
            value = int(re.match(r'\d+', part_str).group(0))
            
            if 'ч.' in part_str:
                total_mute_seconds += value * 3600
            elif 'м.' in part_str:
                total_mute_seconds += value * 60
            elif 'с.' in part_str:
                total_mute_seconds += value
    
    mute_expiry_datetime = datetime.now() + timedelta(seconds=total_mute_seconds) if total_mute_seconds != 0 else zero_datetime()

    try:
        await app.restrict_chat_member(message.chat.id, target_user_id, types.ChatPermissions(can_send_message=False), mute_expiry_datetime)
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')
    
    if total_mute_seconds == 0 or total_mute_seconds > 31622400 or total_mute_seconds < 30:
        await message.edit_text(f'Вы заглушили пользователя {user_first_name} на: **навсегда**.')
    else:
        _hours = total_mute_seconds // 3600
        _minutes = (total_mute_seconds % 3600) // 60
        _seconds = total_mute_seconds % 60

        _text = ""

        if int(_hours) > 0:
            _text += f"{_hours}ч. "
        
        if int(_minutes) > 0:
            _text += f"{_minutes}м. "
        
        if _seconds > 0:
            _text += f"{_seconds}с."

        await message.edit_text(f'Вы заглушили пользователя {user_first_name} на: **{_text}**')

@func(filters.command('unmute', ['.', '!', '/']) & filters.me)
async def unmute_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.mention
    else:
        try:
            user_identifier_str = message.text.split(' ')[1]
        except IndexError:
            return await message.edit_text('Вы не указали параметры: {ответ на сообщение/айди/@юзер} {время(не обязательно)}')

        if user_identifier_str.isnumeric():
            target_user_id = int(user_identifier_str)

            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            user_first_name = chat_member.user.mention
        else:
            if '@' in user_identifier_str:
                user_identifier_str = user_identifier_str.replace('@', '')
            
            chat_member = await app.get_chat_member(message.chat.id, user_identifier_str)
            target_user_id = chat_member.user.id
            user_first_name = chat_member.user.mention
    
    try:
        await app.restrict_chat_member(message.chat.id, target_user_id, types.ChatPermissions(can_send_messages=True))
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')

    await message.edit_text(f'Вы сняли мут с пользователя {user_first_name}')

@func(filters.command('addgroup', ['.', '!', '/']) & filters.me, 'Добавляет в список группу, где вы находитесь, на модерацию.')
async def set_group_on_moder(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    if str(message.chat.id) in config['groups']:
        return await message.edit_text('Эта группа уже зарегистрирована.')
    
    config['groups'].append(str(message.chat.id))

    config._save()

    await message.edit_text('Эта группа зарегистрирована.')

@func(filters.command('addword', ['.', '!', '/']) & filters.me, description='Добавляет слово к списку запрещённых слов.')
async def add_word(_, message: types.Message):
    try:
        _type = message.text.split()[2]
    except IndexError:
        return await message.edit_text('Вы не верно ввели параметры: /addword <слово(в нижнем регистре)> <тип> <срок(необязательно.в мин.)>')
    
    if _type.lower() == 'kick':
        try:
            word = message.text.split()[1]
        except IndexError:
            return await message.edit_text('Вы не верно ввели параметры: /addword <слово(в нижнем регистре)> kick')
        
        config['censored_words'].append(word)
        config['punishments'].update({word: {"type": "kick"}})
    elif _type.lower() == 'ban':
        try:
            word = message.text.split()[1]

            seconds = message.text.split()[3]
        except IndexError:
            return await message.edit_text('Вы не верно ввели параметры: /addword <слово(в нижнем регистре)> ban <срок(необязательно.в сек.)>')

        if not seconds.isnumeric():
            return await message.edit_text('Вы не верно ввели срок бана: /addword <слово(в нижнем регистре)> ban <срок(необязательно.в сек.)>')
        
        config['censored_words'].append(word)
        config['punishments'].update({word: {"type": "ban", "term": seconds}})
    elif _type.lower() == 'mute':
        try:
            word = message.text.split()[1]

            seconds = int(message.text.split()[3])
        except IndexError:
            return await message.edit_text('Вы не верно ввели параметры: /addword <слово(в нижнем регистре)> mute <срок(необязательно.в сек.)>')
        except ValueError:
            return await message.edit_text('Вы не верно ввели параметры: /addword <слово(в нижнем регистре)> mute <срок(необязательно.в сек. ЦИФРАМИ)>')

        if not seconds.isnumeric():
            return await message.edit_text('Вы не верно ввели срок бана: /addword <слово(в нижнем регистре)> mute <срок(необязательно.в сек.)>')
        
        config['censored_words'].append(word)
        config['punishments'].update({word: {"type": "mute", "term": seconds}})
    
    config._save()

    return await message.edit_text(f'Слово `{word}` добавлен к списку запрещённых слов.', parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('rmgroup', ['.', '!', '/']) & filters.me, 'Удаляет из списка группу, где вы находитесь, на модерацию.')
async def remove_group(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')
    
    user_status = (await app.get_chat_member(message.chat.id, 'me')).status
    
    if user_status != enums.ChatMemberStatus.ADMINISTRATOR and user_status != enums.ChatMemberStatus.OWNER:
        return await message.edit_text('Вы не являетесь владельцем или админом.')
    
    if str(message.chat.id) not in config['groups']:
        return await message.edit_text('Эта группа уже удалена.')
    
    config['group'].pop(config['group'].index(str(message.chat.id)))

    config._save()

@func(filters.command('rmword', ['.', '!', '/']) & filters.me, description='Убирает слово из списка запрещённых слов.')
async def remove_word(app: Client, message: types.Message):
    try:
        word = message.text.split()[1]
    except IndexError:
        return await message.edit_text('Вы не верно ввели параметры: /rmword <слово>')
    
    if word not in config['censored_words']:
        return await message.edit_text(f'Слово: `{word}` нету в списке запрещённых слов.', parse_mode=enums.ParseMode.MARKDOWN)
    
    config['censored_words'].pop(config['censored_words'].index(word))
    config['punishments'].pop(config['punishments'].index(word))

@func(filters.group & chat_id_in_reg)
async def moderation_chat(app: Client, message: types.Message):
    search_censured_word = re.search('|'.join(config['censored_words']), message.text, re.IGNORECASE)
    print(search_censured_word)

    if search_censured_word is not None:
        word = search_censured_word.group(0)
        print(word)

        action = config['punishments'].get(word)

        try:
            if action['type'] == 'kick':
                await app.ban_chat_member(message.chat.id, message.from_user.id)
                await app.unban_chat_member(message.chat.id, message.from_user.id)
                return await message.reply_text(f"Пользователь {message.from_user.mention} был кикнут за запрещенное слово: {word}", parse_mode=enums.ParseMode.HTML)
            elif action['type'] == 'ban':
                seconds = action['term']

                ban_expiry_datetime = datetime.now() + timedelta(seconds=seconds) if seconds > 30 else zero_datetime()

                try:
                    await app.ban_chat_member(message.chat.id, message.from_user.id, ban_expiry_datetime)
                except exceptions.UsernameNotOccupied:
                    return
                except exceptions.UserNotParticipant:
                    return
                except exceptions.UserAdminInvalid:
                    return

                _hours = seconds // 3600
                _minutes = (seconds % 3600) // 60
                _seconds = seconds % 60

                _text = ''

                if int(_hours) > 0:
                    _text += f"{_hours}ч. "
                
                if int(_minutes) > 0:
                    _text += f"{_minutes}м. "
                
                if _seconds > 0:
                    _text += f"{_seconds}с."
                
                if seconds < 31:
                    _text = 'всегда'
                
                return await message.reply_text(f"Пользователь {message.from_user.mention} был заглушён на {_text.strip()} за запрещенное слово: {word}", parse_mode=enums.ParseMode.HTML)
            elif action['type'] == 'mute':
                seconds = action['term']

                mute_expiry_datetime = datetime.now() + timedelta(seconds=seconds) if seconds > 30 else zero_datetime()

                try:
                    await app.restrict_chat_member(message.chat.id, message.from_user.id, types.ChatPermissions(can_send_messages=False), mute_expiry_datetime)
                except exceptions.UsernameNotOccupied:
                    return
                except exceptions.UserNotParticipant:
                    return
                except exceptions.UserAdminInvalid:
                    return

                _hours = seconds // 3600
                _minutes = (seconds % 3600) // 60
                _seconds = seconds % 60

                _text = ''

                if int(_hours) > 0:
                    _text += f"{_hours}ч. "
                
                if int(_minutes) > 0:
                    _text += f"{_minutes}м. "
                
                if _seconds > 0:
                    _text += f"{_seconds}с."
                
                if seconds < 31:
                    _text = 'всегда'
                
                return await message.reply_text(f"Пользователь {message.from_user.mention} был забанен на {_text.strip()} за запрещенное слово: {word}", parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            print(traceback.format_exc())