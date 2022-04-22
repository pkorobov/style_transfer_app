import telebot
import requests


inference_host = '34.88.14.177'

token = 'BOT TOKEN'
bot = telebot.TeleBot(token)
photo = None

user_styles = dict()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        (
            "Hi, this is Style Transfer Bot!\n"
            "You can specify a style to transfer using /choose_style command and "
            "/stylize_content to choose a content image to apply the last specified style"
         )
    )


@bot.message_handler(commands=['choose_style'])
def request_style(message):
    bot.send_message(message.chat.id, "Load style image, please.")
    bot.register_next_step_handler(message, specify_style)
    return


@bot.message_handler(commands=['stylize_content'])
def request_content(message):
    if message.chat.id not in user_styles:
        request_style(message)
        return

    bot.send_message(message.chat.id, "Load an image you want to stylize.")
    bot.register_next_step_handler(message, stylize_content)
    return


def specify_style(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        style_image = bot.download_file(file_info.file_path)
        user_styles[message.chat.id] = style_image
        request_content(message)
    except Exception as e:
        print(f"Exception occurred: {e}")
        bot.send_message(message.chat.id, "Oops... something went unexpected. Try to load image or specify style.")
    return


def stylize_content(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        content_image = bot.download_file(file_info.file_path)
        style_image = user_styles[message.chat.id]
        bot.send_message(message.chat.id, "Wait a sec...")
        response = requests.post(files={"content": content_image, "style": style_image}, url='http://127.0.0.1:1489/generate')
        stylized_image = response.content
        bot.send_photo(message.chat.id, stylized_image)
        bot.send_message(message.chat.id, "Voila!")
        request_content(message)
    except Exception as e:
        print(f"Exception occurred: {e}")
        bot.send_message(message.chat.id, "Oops... something went unexpected. Try to load image or specify style.")
    return


if __name__ == '__main__':
    bot.infinity_polling()
