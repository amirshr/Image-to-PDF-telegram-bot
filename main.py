from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from ImageToPdf import ImageToPdf
from aiogram.types.message import ContentType
from PIL import Image
from UploadToDrive import UploadToDrive
from Database import upload_database, add_user_to_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import shutil
import os
import logging
import time
from datetime import datetime
import asyncio

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))
api_token = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=api_token)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def show_main_list(message: types.Message):
    add_user_to_db(message)
    await message.reply('Hi, now send me the images that you want convert to pdf. '
                        '\n\nyou will be notified about added images,'
                        '\nduplicate images will be ignored.')


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
    user_id = str(message.chat.id)
    try:
        os.makedirs(dir_path + '/UserData/' + user_id)
    except Exception as e:
        print(e)
        pass

    destination = (dir_path + '/UserData/' + user_id + '/' + message.photo[2].file_unique_id + '.jpg')
    if await bot.download_file_by_id(message.photo[2].file_id, destination):

        im_num = 0
        for f in os.scandir(dir_path + '/UserData/' + user_id):
            if f.path[-3:] == 'jpg':
                im_num += 1

        await message.reply(text=f'Your image added! \nnumber of added images: {im_num}',
                            reply_markup=get_convert_and_delete_keyboard())


@dp.callback_query_handler(text='Convert to pdf')
async def convert_to_pdf(query: types.CallbackQuery):
    await query.answer('Processing...')
    images = []
    user_id = str(query.message.chat.id)
    for f in os.scandir(dir_path + '/UserData/' + user_id):
        if f.path[-3:] == 'jpg':
            images.append(Image.open(f.path))
    converter = ImageToPdf(images, dir_path + '/UserData/' + user_id)
    converter.convert()

    await types.ChatActions.upload_document()
    pdf = types.InputFile(dir_path + '/UserData/' + user_id + '/converted.pdf')
    await bot.send_document(query.message.chat.id, pdf)

    uploader = UploadToDrive(user_id)
    uploader.upload()

    delete_user_data(user_id)


def delete_user_data(user_id):
    try:
        shutil.rmtree(dir_path + '/UserData/' + user_id)
    except (FileExistsError, FileNotFoundError):
        pass


@dp.callback_query_handler(text='Remove added images')
async def delete_images(query: types.CallbackQuery):
    user_id = str(query.message.chat.id)
    await query.answer('Added images removed.')
    delete_user_data(user_id)

    await bot.send_message(query.message.chat.id, 'Your added images have been deleted!'
                                                  ' \n\nnow you can send images again.')


async def hour_time():
    print(True, True, datetime.now().hour)

    if datetime.now().hour == 6:
        await asyncio.sleep(6 * 3600)


if __name__ == '__main__':
    print(datetime.now())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(upload_database, "interval", seconds=1200)
    scheduler.add_job(hour_time, 'interval', seconds=60)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
