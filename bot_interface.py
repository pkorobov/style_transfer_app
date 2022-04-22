import telebot
import requests


HOST = "http://127.0.0.1:1489"
TOKEN = "BOT TOKEN"
bot = telebot.TeleBot(TOKEN)
user_styles = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    """Defines bot actions on /start command

    Args:
        message (telebot.types.Message): The structure containing telegram message and its info

    Returns:
        None
    """
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
    """Defines bot actions on /choose_style command

    Args:
        message (telebot.types.Message): The structure containing telegram message and its info

    Returns:
        None
    """
    bot.send_message(message.chat.id, "Load style image, please.")
    bot.register_next_step_handler(message, specify_style)


@bot.message_handler(commands=['stylize_content'])
def request_content(message):
    """Defines bot actions on /stylize_content command

    Args:
        message (telebot.types.Message): The structure containing telegram message and its info

    Returns:
        None
    """
    if message.chat.id not in user_styles:
        request_style(message)
        return

    bot.send_message(message.chat.id, "Load an image you want to stylize.")
    bot.register_next_step_handler(message, stylize_content)


def specify_style(message):
    """Puts a photo sent by user into user_styles dictionary

    Args:
        message (telebot.types.Message): The structure containing telegram message and its info

    Returns:
        None
    """
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        style_image = bot.download_file(file_info.file_path)
        user_styles[message.chat.id] = style_image
        request_content(message)
    except (TypeError, AttributeError, IndexError) as e:
        print(f"Exception occurred: {e}")
        bot.send_message(
            message.chat.id,
            "Oops... something went unexpected. Try to load image or specify style."
        )


def stylize_content(message):
    """Takes a content image from user's message and runs neural network on it

    Args:
        message (telebot.types.Message): The structure containing telegram message and its info

    Returns:
        None
    """
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        content_image = bot.download_file(file_info.file_path)
        style_image = user_styles[message.chat.id]
        bot.send_message(message.chat.id, "Wait a sec...")
        response = requests.post(
            files={"content": content_image, "style": style_image},
            url=f'{HOST}/generate'
        )
        stylized_image = response.content
        bot.send_photo(message.chat.id, stylized_image)
        bot.send_message(message.chat.id, "Voila!")
        request_content(message)
    except (TypeError, AttributeError, IndexError) as e:
        print(f"Exception occurred: {e}")
        bot.send_message(
            message.chat.id,
            "Oops... something went unexpected. Try to load image or specify style."
        )


if __name__ == "__main__":
    bot.infinity_polling()
