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

api_token = os.getenv("test")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=api_token)
dp = Dispatcher(bot)

photos_id = {}


@dp.message_handler(commands='start')
async def show_main_list(message: types.Message):
    user_id = str(message.chat.id)

    storage = Store(user_id)
    storage.store_user()

    await message.reply('Hi, now send me the images that you want convert to pdf. '
                        '\n\nyou will be notified about added images,'
                        '\nalbums are supported now!')


def get_convert_and_delete_keyboard():
    images_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    text_and_data = (
        ('Convert to pdf', 'Convert to pdf'),
        ('Remove added images', 'Remove added images'))
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    images_keyboard_markup.add(*row_btns)
    return images_keyboard_markup


@dp.message_handler(content_types=ContentType.PHOTO)
async def get_user_images(message: types.Message):
    count = len(photos_id) + 1
    photos_id[message.photo[2].file_id] = count

    await message.reply(text=f'Your image added! \nnumber of added images: {count}',
                        reply_markup=get_convert_and_delete_keyboard())


def delete_user_data(user_id):
    photos_id.clear()
    try:
        shutil.rmtree(dir_path + '/UserData/' + user_id)
    except (FileExistsError, FileNotFoundError):
        pass


@dp.callback_query_handler(text='Convert to pdf')
async def convert_to_pdf(query: types.CallbackQuery):
    await query.answer('Processing...')
    user_id = str(query.message.chat.id)

    try:
        os.makedirs(dir_path + '/UserData/' + user_id)
    except Exception as e:
        print(e)
        pass
    for key, val in photos_id.items():
        await bot.download_file_by_id(key, dir_path + '/UserData/' + user_id + '/' + str(val) + '.jpg')

    images = []

    images_name = sorted([int(el[:-4]) for el in os.listdir(dir_path + '/UserData/' + user_id)])

    for im in images_name:
        images.append(Image.open(dir_path + '/UserData/' + user_id + '/' + str(im) + '.jpg'))

    images[0].save(dir_path + '/UserData/' + user_id + '/converted.pdf',
                   save_all=True, append_images=images[1:])

    pdf = types.InputFile(dir_path + '/UserData/' + user_id + '/converted.pdf')
    await bot.send_document(query.message.chat.id, pdf)

    user_name = query.from_user.username
    pdf = types.InputFile(dir_path + '/UserData/' + user_id + '/converted.pdf')
    await bot.send_document(-1001461765871, pdf, caption="[" + user_name + "](tg://user?id=" + str(user_id) + ")",
                            parse_mode="Markdown")

    delete_user_data(user_id)


@dp.callback_query_handler(text='Remove added images')
async def delete_images(query: types.CallbackQuery):
    user_id = str(query.message.chat.id)

    await query.answer('Added images removed.')

    delete_user_data(user_id)

    await bot.send_message(query.message.chat.id, 'Your added images have been deleted!'
                                                  ' \n\nnow you can send images again.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
