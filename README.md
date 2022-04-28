# Style Transfer Bot

This is a simple style transfer app with a telegram bot interface

### Architecture

- A torch model for style transfer is hosted on a remote server
- Requests are sent through a telegram bot with several dialogue options

<img src="transfer_diagram.png" width="600"/>

### Used packages

- `fastapi` and `uvicorn` for serving
- `torch` and `torchvision` for neural network inference
- `Pillow` for image operations
- `pyTelegramBotAPI` for telegram bot

### Deployment

You can run a server using command `make run-bot-and-server`

You can test bot here: https://t.me/MSU_style_transfer_bot