import face_recognition
import subprocess
import tempfile
from vars import *
import telebot
import requests
import os

bot = telebot.TeleBot(TOKEN)


def convert(uid, in_bytes=None, out_name='out.wav'):
    # Функция конвертации из .ogg в .wav
    in_filename = None
    if in_bytes:
        temp_in_file = tempfile.NamedTemporaryFile(delete=False)  #Создание временного файла для конвертации
        temp_in_file.write(in_bytes)
        in_filename = temp_in_file.name
        temp_in_file.close()

    # Запрос в командную строку для обращения к FFmpeg
    command = [
        'ffmpeg',
        '-i', in_filename,
        '-f', 'wav',
        '-ar', '16000',
        r'/home/nail/' + str(uid) + '/' + out_name
    ]
    proc = subprocess.Popen(command)
    proc.wait()
    os.remove(in_filename)



@bot.message_handler(content_types=["voice"])
def voice(message):
    # Получение голосового сообщения
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
    if not os.path.exists('/home/usr/'+str(message.chat.id)):
        dir_name = r'/home/usr/'+str(message.chat.id)
        os.makedirs(dir_name)
        with open(r'/home/usr/' + str(message.chat.id) + '/count.txt','w') as count:
            count.write('1')
            convert(message.chat.id, file.content, 'audio_message_0.wav')
            bot.reply_to(message, 'Аудосообщение сохранено как audio_message_0.wav')
    else:
        with open(r'/home/usr/' + str(message.chat.id) + '/count.txt', 'r') as count:
            n = int(count.read())
        with open(r'/home/usr/' + str(message.chat.id) + '/count.txt', 'w') as count:
            count.write(str(n + 1))
            convert(message.chat.id ,file.content,'audio_message_{}.wav'.format(n))
            bot.reply_to(message, 'Аудосообщение сохранено как audio_message_{}.wav'.format(n))

@bot.message_handler(content_types=["photo"])
def face(message):
    # Получение фотографии
    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
    temp_in_file = tempfile.NamedTemporaryFile(delete=False)
    temp_in_file.write(file.content)
    in_filename = temp_in_file.name
    temp_in_file.close()

    image = face_recognition.load_image_file(in_filename)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) != 0:
        dir_name = r'/home/usr/' + str(message.chat.id)
        if not os.path.exists(dir_name + '/photos'):
            os.makedirs(dir_name + '/photos')
        with open(dir_name + '/' + file_info.file_path, 'wb') as new_file:
            new_file.write(file.content)
        bot.reply_to(message, "На фото лицо, фото добавлено")
    else:
        bot.reply_to(message, "На фото нет лица, фото не добавлено")
    os.remove(in_filename)


if __name__ == '__main__':
    bot.polling(none_stop=True)