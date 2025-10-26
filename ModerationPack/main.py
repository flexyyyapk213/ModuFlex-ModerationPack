from loads import func
from pyrogram.client import Client
from pyrogram import filters
from pyrogram import types
from pyrogram.utils import zero_datetime
from pyrogram import enums
import re
from datetime import datetime, timedelta
from pyrogram.errors import exceptions

@func(filters.command('ban', prefixes=['.', '!', '/']) & filters.me)
async def ban_user(app: Client, message: types.Message):
    if message.chat.type != enums.ChatType.GROUP and message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.edit_text('Эта команда работает в чате.')

    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
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
            user_first_name = chat_member.user.first_name
    
    if not message.reply_to_message:
        duration_input_str = ' '.join(message.text.split(' ')[2:])
    else:
        duration_input_str = ' '.join(message.text.split(' ')[1:])

    total_ban_seconds: int = 0
    
    if duration_input_str.isnumeric():
        total_ban_seconds = int(duration_input_str)
    elif duration_input_str:
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
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
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
            user_first_name = chat_member.user.first_name
    
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
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
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
            user_first_name = chat_member.user.first_name
    
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
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
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
            user_first_name = chat_member.user.first_name
    
    if not message.reply_to_message:
        duration_input_str = ' '.join(message.text.split(' ')[2:])
    else:
        duration_input_str = ' '.join(message.text.split(' ')[1:])

    total_mute_seconds: int = 0
    
    if duration_input_str.isnumeric():
        total_mute_seconds = int(duration_input_str)
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
        await app.restrict_chat_member(message.chat.id, target_user_id, types.ChatPermissions(), mute_expiry_datetime)
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
    
    target_user_id: int = None
    user_first_name: str = None

    if message.reply_to_message is not None:
        target_user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
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
            user_first_name = chat_member.user.first_name
    
    try:
        await app.restrict_chat_member(message.chat.id, target_user_id, types.ChatPermissions(can_send_messages=True))
    except exceptions.UsernameNotOccupied:
        return await message.edit_text('Такого пользователя нету.')
    except exceptions.UserNotParticipant:
        return await message.edit_text('Такого пользователя нету в чате.')
    except exceptions.UserAdminInvalid:
        return await message.edit_text('Вы не являетесь админом в этом чате.')

    await message.edit_text(f'Вы сняли мут с пользователя {user_first_name}')