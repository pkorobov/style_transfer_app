"""server.py is a script that runs FastAPI server with a neural network."""

import os
import tempfile

import torch
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from torchvision import transforms
from torchvision.utils import save_image

from style_transfer_app.utils import style_transfer


def write_file(data, path):
    """Write a byte file to the specified path.

    Args:
        data (bytes): data to be written.
        path (str): path to write data to.

    """
    with open(path, "wb") as f:
        f.write(data.read())


decoder_path = os.path.join(os.path.dirname(__file__), "models/decoder.pt")
decoder = torch.jit.load(decoder_path)
decoder.eval()

vgg_path = os.path.join(os.path.dirname(__file__), "models/vgg.pt")
vgg = torch.jit.load(vgg_path)
vgg.eval()

trans = transforms.ToTensor()

app = FastAPI()


@app.post("/generate")
def generate(style: UploadFile, content: UploadFile):
    """Process requests to return a stylized image.

    Args:
        style (fastapi.UploadFile): A container with style image data.
        content (fastapi.UploadFile): A container with content image data.

    Returns:
       FileResponse.
       A container with stylized image data.

    """
    style_format = style.content_type.split("/")[-1]
    content_format = content.content_type.split("/")[-1]
    style_name = "style." + style_format
    content_name = "content." + content_format
    result_name = "result.png"
    # alpha = float(data.alpha)
    alpha = 1.0

    with tempfile.TemporaryDirectory() as tmp_dir:
        style_name = os.path.join(tmp_dir, style_name)
        content_name = os.path.join(tmp_dir, content_name)
        # result_name = os.path.join(tmp_dir, result_name)
        write_file(style.file, style_name)
        write_file(content.file, content_name)
        content = trans(Image.open(content_name))
        style = trans(Image.open(style_name))

    # if data.preserve_color:
    #    style = coral(style, content)
    style = style.unsqueeze(0)
    content = content.unsqueeze(0)
    with torch.no_grad():
        output = style_transfer(vgg, decoder, content, style, alpha)
    save_image(output, result_name)
    return FileResponse(result_name)
