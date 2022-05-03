"""__main__ runs server and bot simultaneously."""

import argparse
import threading
import uvicorn
from style_transfer_app.bot_interface import StyleTransferBot


def main():
    """Start server in background and then run bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--token')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=1489)
    args = parser.parse_args()

    bot = StyleTransferBot(token=args.token, host=f'http://{args.host}:{args.port}')
    thread = threading.Thread(target=bot.infinity_polling)
    thread.start()
    uvicorn.run("style_transfer_app.server:app", host=args.host, port=args.port)
    thread.join()


main()
