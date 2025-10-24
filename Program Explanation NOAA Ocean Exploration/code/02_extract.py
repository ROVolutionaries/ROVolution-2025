#https://www.youtube.com/watch?v=mRhQmRm_egc

import os
from glob import glob
import pandas as pd
from functools import reduce
import json
from shutil import move
import yaml

def extract_json(filename):
    json_file_path = filename
    parser = []

    with open(json_file_path, "r") as file:
        data = json.load(file)

    for file in data:
        filename = os.path.join(file["uuid"] + ".png")

        imgwidth = file["width"]
        imgheight = file["height"]

        for box in file["boundingBoxes"]:
            name = box["concept"]

            boxx = box["x"]
            boxy = box["y"]
            boxwidth = box["width"]
            boxheight = box["height"]

            parser.append([filename, imgwidth, imgheight, name, boxwidth, boxheight, boxx, boxy])

    return parser

df = pd.DataFrame(extract_json("data.json"), columns = ["filename", "imgwidth", "imgheight", "name", "boxwidth", "boxheight", "boxx", "boxy"])
#df.info()
#df["name"].value_counts()

columns = ["filename", "imgwidth", "imgheight", "name", "boxwidth", "boxheight", "boxx", "boxy"]

df["center_x"] = ((df["boxwidth"] / 2 + df["boxx"]) / df["imgwidth"])
df["center_y"] = ((df["boxheight"] / 2 + df["boxy"]) / df["imgheight"])

df["w"] = df["boxwidth"] / df["imgwidth"]
df["h"] = df["boxheight"] / df["imgheight"]
#df.head()

unique_names = df["name"].unique()

labels = dict()
for num in range(len(unique_names)):
    labels[unique_names[num]] = num

df["id"] = df["name"].map(labels)

images = df['filename'].unique()
#len(images)

img_df = pd.DataFrame(images, columns=['filename'])
#img_df.head()

img_train = tuple(img_df.sample(frac=0.8)['filename'])
#shuffling data and picking 80% of images

#picking all images that were not in the 80% train set (the other 20%)
img_test = tuple(img_df[~img_df['filename'].isin(img_train)]['filename'])
#len(img_train), len(img_test) #length of each set

#making dataframes
train_df = df.query(f'filename in {img_train}')
test_df = df.query(f'filename in {img_test}')

os.makedirs("images/images/train", exist_ok=True)
os.makedirs("images/images/val", exist_ok=True)
os.makedirs("images/labels/train", exist_ok=True)
os.makedirs("images/labels/val", exist_ok=True)

columns = ["filename", "id", "center_x", "center_y", "w", "h"]
groupby_obj_train = train_df[columns].groupby("filename")
groupby_obj_test = test_df[columns].groupby("filename")

def save_data(filename, images_folder_path, labels_folder_path, group_obj):
    source = os.path.join("images", filename)
    destination = os.path.join(images_folder_path, filename)
    move(source, destination)

    text_filename = os.path.join(labels_folder_path,os.path.splitext(filename)[0] + ".txt")
    group_obj.get_group(filename).set_index("filename").to_csv(text_filename,sep=' ',index=False,header=False)

filename_series_train = pd.Series(groupby_obj_train.groups.keys())
filename_series_train.apply(save_data,args=("images/images/train","images/labels/train",groupby_obj_train))

filename_series_test = pd.Series(groupby_obj_test.groups.keys())
filename_series_test.apply(save_data,args=("images/images/val","images/labels/val",groupby_obj_test))

data = {
    'train': 'images/images/train',
    'val': 'images/images/test',
    'nc': len(labels),
    'names': list(labels.keys())
}

with open('data.yaml', 'w') as file:
    yaml.dump(data, file, default_flow_style=False, sort_keys=False)
