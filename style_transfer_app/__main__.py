import subprocess
import argparse
from style_transfer_app.bot_interface import StyleTransferBot


def main():
    """Start server in background and then run bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--token')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=1489)
    args = parser.parse_args()

    with subprocess.Popen([
            "uvicorn",
            "style_transfer_app.server:app",
            f"--host={args.host}",
            f"--port={args.port}",
            "--reload"
    ]):
        bot = StyleTransferBot(token=args.token, host=f'http://{args.host}:{args.port}')
        bot.infinity_polling()


main()
