  
import discord
import json
import numpy as np
import random
import string
import Augmentor
import os
import shutil
import asyncio
import time
from PIL import ImageFont, ImageDraw, Image
     
           
# Create captcha
image = np.zeros(shape= (100, 350, 3), dtype= np.uint8)

# Create image 
image = Image.fromarray(image+255) # +255 : black to white

# Add text
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(font= "Tools/arial.ttf", size= 60)

text = ' '.join(random.choice(string.ascii_uppercase) for _ in range(6)) # + string.ascii_lowercase + string.digits

# Center the text
W, H = (350,100)
w, h = draw.textsize(text, font= font)
draw.text(((W-w)/2,(H-h)/2), text, font= font, fill= (90, 90, 90))

# Save
folderPath = "C:/Users/msm67/Downloads/test"
image.save(f"C:/Users/msm67/Downloads/test/image.png")

"""
p = Augmentor.Pipeline(folderPath)
p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
p.process()
"""
# Search file in folder
path = "C:/Users/msm67/Downloads/test/output"

image = Image.open(f"C:/Users/msm67/Downloads/test/image.png")

"""# Add line
width = random.randrange(6, 8)
co1 = random.randrange(0, 75)
co3 = random.randrange(275, 350)
co2 = random.randrange(40, 65)
co4 = random.randrange(40, 65)
draw = ImageDraw.Draw(image)
draw.line([(co1, co2), (co3, co4)], width= width, fill= (90, 90, 90))

# Add noise
noisePercentage = 0.25 # 25%

pixels = image.load() # create the pixel map
for i in range(image.size[0]): # for every pixel:
    for j in range(image.size[1]):
        rdn = random.random() # Give a random %
        if rdn < noisePercentage:
            pixels[i,j] = (90, 90, 90)"""

# Save
image.save(f"C:/Users/msm67/Downloads/test/output/image.png")