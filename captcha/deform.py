from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import string
from io import BytesIO
import os
from test import WaveDeformer
import random
print(random.random())



print(' '.join(random.choice(string.ascii_uppercase) for i in range(6))) # + string.ascii_lowercase + string.digits)

img = Image.new(size=(350, 100), color=255, mode="L")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(font= "Tools/arial.ttf", size= 60)

text = ' '.join(random.choice(string.ascii_uppercase) for i in range(6))
W, H = (350, 100)
w, h = draw.textsize(text, font= font)
draw.text(((W-w)/2,(H-h)/2), text, font= font, fill=0)
img=ImageOps.deform(img, WaveDeformer())

img.paste(255, [109, 0, 220, 13])
img.paste(255, [0, 85, 109, 100])
img.paste(255, [328, 0, 350, 7])
img.paste(255, [216, 85, 331, 100])

width = random.randrange(10, 15)
co1 = random.randrange(25, 88)
co2 = random.randrange(20, 80)
co3 = random.randrange(268, 334)
co4 = random.randrange(11, 40)
print((co1, co2), (co3, co4))
draw = ImageDraw.Draw(img)
draw.line([(co1, co2), (co3, co4)], width= width, fill=90)


randomization = .30

xsize, ysize = img.size
pix = img.load()
for x in range(xsize):
    for y in range(ysize):
        perc = random.random()
        if perc < randomization:
            pix[x, y] = 90
#img.show()
#im.save("image.png")










"""p = Augmentor.DataPipeline(image)
p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
p.process
print(p)
bytes = BytesIO()
image.save(bytes, "png")
bytes = bytes.getvalue()
ImageShow.show(Image.fromarray(np.uint8(255 * p.keras_preprocess_func())))
image.save("img.png")"""

"""
# Add text
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(font= "Tools/arial.ttf", size= 60)

text = ' '.join(random.choice(string.ascii_uppercase) for _ in range(6)) # + string.ascii_lowercase + string.digits

# Center the text
W, H = (350,100)
w, h = draw.textsize(text, font= font)
draw.text(((W-w)/2,(H-h)/2), text, font= font, fill= (90, 90, 90))
image.save("img.png")"""