from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os
import torch
from PIL import Image
from function import style_transfer, coral
from torchvision.utils import save_image
from torchvision import transforms


def write_file(data, path):
    """Writes byte file to specified path.

    Args:
        data (bytes): data to be written.
        path (str): path to write data to.
    """

    with open(path, "wb") as f:
        f.write(data.read())


decoder = torch.load("data/decoder.pt")
vgg = torch.load("data/vgg.pt")
decoder.eval()
vgg.eval()
trans = transforms.ToTensor()

app = FastAPI()


@app.post("/generate")
def main(style: UploadFile, content: UploadFile):
    """Processes requests to return stylized image.

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