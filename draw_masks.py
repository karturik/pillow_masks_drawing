import shutil
import xml.etree.ElementTree as ET
from tqdm import tqdm
from PIL import Image, ImageDraw
import os


images_dir = ''

# GET COLORS FROM ANNOTATION FILE
def get_colors(xml_path):
    xml_ann = ET.parse(xml_path)
    colors = {}
    labels = xml_ann.find('meta').find('task').find('labels').findall('label')
    for i in labels:
        cls = i.find('name').text
        color = i.find('color').text
        colors[cls] = color
    return colors

# DRAW MASK BY COORDINATES
def vizual_markup(polygons, image, color):
    end_lst_points = []
    for point in polygons:
        x1, y1 = point
        end_lst_points.append((float(x1), float(y1)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.polygon(end_lst_points, fill=color)

# ERASE PART BY COORDINATES
def erase_markup(polygons, image, type):
    if type == 'black':
        second_image = Image.new("RGB", image.size)
    else:
        second_image = Image.open(f"images/{type}")
    end_lst_points = []
    for point in polygons:
        x1, y1 = point
        end_lst_points.append((float(x1), float(y1)))
    draw = ImageDraw.Draw(image, "RGBA")
    mask_im = Image.new("L", image.size, 0)
    draw_erase = ImageDraw.Draw(mask_im)
    draw_erase.polygon(end_lst_points, fill=255)
    image.paste(second_image, box=(0,0), mask=mask_im)

# DRAW MASKS ON BLACK BACKGROUND
def get_masks_on_black(task_number):
    root = ET.parse('annotations.xml')
    clrs = get_colors('annotations.xml')
    for img in tqdm(root.findall('image')):
        if len(img.findall('tag')) == 0:
            name = os.path.basename(img.attrib['name'])
            polygons = img.findall('polygon')
            w_img, h_img = int(img.attrib['width']), int(img.attrib['height'])
            created_image = Image.new("RGB", (w_img, h_img))
            w1, h1 = created_image.size
            img.attrib['width'] = str(w1)
            img.attrib['height'] = str(h1)
            ignore_polygons = []
            for pol in polygons:
                if pol.attrib['label'] == 'flore':
                    pol_name = pol.attrib['label']
                    points = [i.split(',') for i in pol.attrib['points'].split(';')]
                    vizual_markup(points, created_image, "#ffffff")
                else:
                     ignore_polygons.append(pol)
            for pol in ignore_polygons:
                pol_name = pol.attrib['label']
                points = [i.split(',') for i in pol.attrib['points'].split(';')]
                type = 'black'
                vizual_markup(points, created_image, "#000000")
            out_d = 'masks'
            if not os.path.exists(out_d):
                os.makedirs(out_d)
            created_image.save(os.path.join(out_d, f"{name.split('.')[0]}.png"))

    for i in os.listdir('masks'):
        try:
            os.rename(os.path.join('masks', i), os.path.join('masks', i.replace('image', 'mask')))
        except:
            pass
    shutil.make_archive(f'masks_{task_number}', 'zip', 'masks')
    shutil.rmtree('masks', ignore_errors=True)
    shutil.rmtree('ann', ignore_errors=True)

# DRAW MASKS ON PHOTO
def get_masks_on_photo(task_number):
    root = ET.parse('annotations.xml')
    clrs = get_colors('annotations.xml')
    for img in tqdm(root.findall('image')):
        if len(img.findall('tag')) == 0:
            name = os.path.basename(img.attrib['name'])
            if name in os.listdir(images_dir):
                polygons = img.findall('polygon')
                created_image = Image.open(f"images/{name}")
                ignore_polygons = []
                for pol in polygons:
                    if pol.attrib['label'] != 'Ignore':
                        pol_name = pol.attrib['label']
                        points = [i.split(',') for i in pol.attrib['points'].split(';')]
                        vizual_markup(points, created_image, clrs[pol_name])
                    else:
                        points = [i.split(',') for i in pol.attrib['points'].split(';')]
                        type = name
                        erase_markup(points, created_image, type)
                out_d = 'masks_on_photo'
                if not os.path.exists(out_d):
                    os.makedirs(out_d)
                created_image.save(os.path.join(out_d, f"{name.split('.')[0]}.png"))
        else:
            print(img, ' tag "No skin" find')
    for i in os.listdir('masks_on_photo'):
        try:
            os.rename(os.path.join('masks_on_photo', i), os.path.join('masks_on_photo', i.replace('masks_on_photo', 'mask')))
        except:
            pass
    shutil.make_archive(f'masks_on_photo{task_number}', 'zip', 'masks_on_photo')
    shutil.rmtree('masks_on_photo', ignore_errors=True)
    shutil.rmtree('ann', ignore_errors=True)


get_masks_on_photo(1414)
get_masks_on_black(1570)

numbers = open('frame_list.txt', 'r', encoding='utf-8').read().strip()