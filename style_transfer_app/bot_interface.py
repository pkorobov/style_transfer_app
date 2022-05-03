"""bot_interface.py contains StyleTransferBot class."""

import telebot
import requests


class StyleTransferBot(telebot.TeleBot):
    """Style Transfer Bot class.

    Args:
        token: telegram bot token given by @BotFather
        host: host with a model running, 127.0.0.1 by default
    """

    def __init__(self, token, host="http://127.0.0.1:1489"):
        """Initialize the user_styles dict and create a bot instance.

        Args:
            token: telegram bot token given by @BotFather
            host: host with a model running, 127.0.0.1 by default
        """
        super().__init__(token)
        self.host = host
        self.user_styles = {}

        @self.message_handler(commands=['start'])
        def start_message(message):
            """Define bot actions on /start command.

            Args:
                message (telebot.types.Message): The structure containing telegram message and its info

            Returns:
                None
            """
            self.send_message(
                message.chat.id,
                (
                    "Hi, this is Style Transfer Bot!\n"
                    "You can specify a style to transfer using /choose_style command and "
                    "/stylize_content to choose a content image to apply the last specified style"
                 )
            )

        @self.message_handler(commands=['choose_style'])
        def request_style(message):
            """Define bot actions on /choose_style command.

            Args:
                message (telebot.types.Message): The structure containing telegram message and its info

            Returns:
                None
            """
            self.send_message(message.chat.id, "Load style image, please.")
            self.register_next_step_handler(message, specify_style)

        @self.message_handler(commands=['stylize_content'])
        def request_content(message):
            """Define bot actions on /stylize_content command.

            Args:
                message (telebot.types.Message): The structure containing telegram message and its info

            Returns:
                None
            """
            if message.chat.id not in self.user_styles:
                request_style(message)
                return

            self.send_message(message.chat.id, "Load an image you want to stylize.")
            self.register_next_step_handler(message, stylize_content)

        def specify_style(message):
            """Put a photo sent by user into user_styles dictionary.

            Args:
                message (telebot.types.Message): The structure containing telegram message and its info

            Returns:
                None
            """
            try:
                file_info = self.get_file(message.photo[-1].file_id)
                style_image = self.download_file(file_info.file_path)
                self.user_styles[message.chat.id] = style_image
                request_content(message)
            except (TypeError, AttributeError, IndexError) as e:
                print(f"Exception occurred: {e}")
                self.send_message(
                    message.chat.id,
                    "Oops... something went unexpected. Try to load image or specify style."
                )

        def stylize_content(message):
            """Take a content image from user's message and runs neural network on it.

            Args:
                message (telebot.types.Message): The structure containing telegram message and its info

            Returns:
                None
            """
            try:
                file_info = self.get_file(message.photo[-1].file_id)
                content_image = self.download_file(file_info.file_path)
                style_image = self.user_styles[message.chat.id]
                self.send_message(message.chat.id, "Wait a sec...")
                response = requests.post(
                    files={"content": content_image, "style": style_image},
                    url=f'{self.host}/generate'
                )
                stylized_image = response.content
                self.send_photo(message.chat.id, stylized_image)
                self.send_message(message.chat.id, "Voila!")
                request_content(message)
            except (TypeError, AttributeError, IndexError) as e:
                print(f"Exception occurred: {e}")
                self.send_message(
                    message.chat.id,
                    "Oops... something went unexpected. Try to load image or specify style."
                )
