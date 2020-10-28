from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from aiogram.types.message import ContentType
from PIL import Image
from store import Store
import shutil
import os
import logging

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))

channel_id = -1001461765871

api_token = os.getenv("API_TOKEN")
# api_token = os.getenv("test")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=api_token)
dp = Dispatcher(bot)

photos_id = {}
pdf_names = {}


@dp.message_handler(commands='start')
async def show_main_list(message: types.Message):
    user_id = str(message.chat.id)

    storage = Store(user_id)
    storage.store_user()

    await message.reply('Hi, now send me the images that you want convert to PDF. '
                        '\n\nyou will be notified about added images,'
                        '\n\nif you need high quality PDF send images as file!'
                        '\n\nreport issues to the developer contact(@ImgDeveloperContactBot), Thanks!')


def get_convert_and_delete_keyboard():
    images_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    text_and_data = (
        ('Convert to pdf', 'Convert to pdf'),
        ('Remove added images', 'Remove added images'))
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    images_keyboard_markup.add(*row_btns)
    return images_keyboard_markup


def get_rename_pdf_keyboard():
    images_keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Yes!', 'yes'),
        ('No!', 'no'))
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    images_keyboard_markup.add(*row_btns)
    return images_keyboard_markup


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def get_user_images_hq(message: types.Message):
    if message.document.mime_type.split('/')[0] == 'image':
        user_id = str(message.chat.id)
        count = 1

        for key, val in photos_id.items():
            if list(val.keys())[0] == user_id:
                count += 1
        try:
            photos_id[message.document.file_id] = {user_id: count}
        except Exception as e:
            print(e)
            pass

        await message.reply(text=f'Your image added! \nnumber of added images: {count}',
                            reply_markup=get_convert_and_delete_keyboard())


@dp.message_handler(content_types=ContentType.PHOTO)
async def get_user_images(message: types.Message):
    user_id = str(message.chat.id)
    count = 1

    for key, val in photos_id.items():
        if list(val.keys())[0] == user_id:
            count += 1
    try:
        photos_id[message.photo[2].file_id] = {user_id: count}
    except IndexError:
        try:
            photos_id[message.photo[1].file_id] = {user_id: count}
        except IndexError:
            photos_id[message.photo[0].file_id] = {user_id: count}

    await message.reply(text=f'Your image added! \nnumber of added images: {count}',
                        reply_markup=get_convert_and_delete_keyboard())


def delete_user_data(user_id):
    user_photos_to_remove = []

    for key, val in photos_id.items():
        if list(val.keys())[0] == user_id:
            user_photos_to_remove.append(key)

    for el in user_photos_to_remove:
        del photos_id[el]

    try:
        shutil.rmtree(dir_path + '/UserData/' + user_id)
    except (FileExistsError, FileNotFoundError):
        pass

    try:
        pdf_names.pop(user_id)
    except KeyError:
        pass


@dp.callback_query_handler(text='Convert to pdf')
async def convert_to_pdf(query: types.CallbackQuery):
    await query.answer('')
    await bot.send_message(query.message.chat.id, 'Do you want to set pdf name?',
                           reply_markup=get_rename_pdf_keyboard())


@dp.callback_query_handler(text='yes')
async def send_pdf_name(query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=query.message.chat.id, text='Send you\'r prefer name:',
                                message_id=query.message.message_id)
    await query.answer('')


@dp.message_handler()
async def set_pdf_name(message: types.Message):
    user_id = str(message.chat.id)
    pdf_names[user_id] = message.text

    try:
        pdf_path = f'{dir_path}/UserData/{user_id}/{pdf_names[user_id]}.pdf'
        await image_to_pdf(user_id, pdf_path)

    except KeyError:
        print(KeyError)
        pdf_path = f'{dir_path}/UserData/{user_id}/converted.pdf'
        await image_to_pdf(user_id, pdf_path)

    except IndexError:
        await bot.send_message(message.chat.id, 'Please send you\'r images...')
        return

    pdf = types.InputFile(pdf_path)
    await bot.send_document(user_id, pdf)

    pdf = types.InputFile(pdf_path)
    await bot.send_document(-1001461765871, pdf, caption="[ user ](tg://user?id=" + str(user_id) + ")",
                            parse_mode="Markdown")

    delete_user_data(user_id)


@dp.callback_query_handler(text='no')
async def convert_to_pdf(query: types.CallbackQuery):
    await query.answer('Processing...')
    await bot.edit_message_text(chat_id=query.message.chat.id, text='Processing...',
                                message_id=query.message.message_id)
    user_id = str(query.message.chat.id)

    try:
        pdf_path = f'{dir_path}/UserData/{user_id}/{pdf_names[user_id]}.pdf'
        await image_to_pdf(user_id, pdf_path)

    except KeyError:
        try:
            pdf_path = f'{dir_path}/UserData/{user_id}/converted.pdf'
            await image_to_pdf(user_id, pdf_path)

        except IndexError:
            await bot.send_message(query.message.chat.id, 'Please send you\'r images...')
            return

    except IndexError:
        await bot.send_message(query.message.chat.id, 'Please send you\'r images...')
        return

    pdf = types.InputFile(pdf_path)
    await bot.send_document(user_id, pdf)

    pdf = types.InputFile(pdf_path)
    await bot.send_document(-1001461765871, pdf, caption="[ user ](tg://user?id=" + str(user_id) + ")",
                            parse_mode="Markdown")

    delete_user_data(user_id)


async def image_to_pdf(user_id, pdf_path):
    try:
        os.makedirs(dir_path + '/UserData/' + user_id)
    except FileExistsError:
        pass

    photos_id.keys()
    for key, val in photos_id.items():

        if list(val.keys())[0] == user_id:
            await bot.download_file_by_id(key, dir_path + '/UserData/' + user_id + '/' + str(val[user_id]) + '.jpg')

    images = []
    try:
        images_name = sorted([int(el[:-4]) for el in os.listdir(dir_path + '/UserData/' + user_id)])

        for im in images_name:
            images.append(Image.open(dir_path + '/UserData/' + user_id + '/' + str(im) + '.jpg'))
        images = [im.convert('RGB') for im in images]
    except Exception as e:
        print(e)
        pass

    images[0].save(pdf_path,
                   save_all=True, append_images=images[1:])
    return True


@dp.callback_query_handler(text='Remove added images')
async def delete_images(query: types.CallbackQuery):
    user_id = str(query.message.chat.id)

    await query.answer('Added images removed.')

    delete_user_data(user_id)

    await bot.send_message(query.message.chat.id, 'Your added images have been deleted!'
                                                  ' \n\nnow you can send images again.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
