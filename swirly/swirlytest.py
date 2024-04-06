import functools
from wand.image import Image
from io import BytesIO
import functools
import asyncio
import urllib

def _swirly(img):
        temp = BytesIO()
        temp.name = "swirlyed.gif"
        with Image() as gif:
            with Image(file=img) as image:
                image.transform(resize="x512")
                for count in range(90):
                    deg = (count * 8)
                    percentage = (100 - count) / 100
                    h = int(image.height * percentage)
                    w = int(image.width * percentage)
                    with image.clone() as swirled:
                        swirled.swirl(degree=deg)
                        swirled.resize(height=image.height, width=image.width)
                        swirled.liquid_rescale(height=h, width=w)
                        swirled.resize(height=image.height, width=image.width)
                        swirled.implode(amount=(-percentage))
                        gif.sequence.append(swirled)
            for frame in gif.sequence:
                frame.delay = 6
            gif.loop = 0
            gif.type = "optimize"
            gif.format = "gif"
            gif.save(temp)
        temp.seek(0)
        return temp

with open("layers.png", "rb") as file:
    with open("swirled.gif", "wb") as swirled:
        swirled.write(_swirly(BytesIO(file.read())).getbuffer())
        