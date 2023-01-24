from PIL import Image
import os
from tqdm import tqdm

dir_with_screenshots = ''


# CUT IMAGE WITH YOUTUBE PLAYER TIMELINE
for n, file in tqdm(enumerate(os.listdir(dir_with_screenshots))):
    name = f"{n}.png"
    print(file)
    working_image = Image.open(f'{dir_with_screenshots}/{file}')
    width, height = working_image.size
    left = 0
    top = 50
    right = width
    bottom = height - 11
    im1 = working_image.crop((left, top, right, bottom))
    im1.save(f'{dir_with_screenshots}/arizona/{name}')
    n += 1


