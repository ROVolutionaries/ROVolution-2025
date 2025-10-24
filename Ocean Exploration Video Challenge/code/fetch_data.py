import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

json_file_path = "ophiuroidea.json"
images_directory = "ophiuroidea/"

os.makedirs(images_directory, exist_ok=True)

with open(json_file_path, "r") as file:
    data = json.load(file)

def download_image(file):
    filename = file["uuid"]
    url = file["url"]
    image_path = os.path.join(images_directory, filename + ".png")

    if not os.path.exists(image_path):
        try:
            response = requests.get(url, timeout=10)  # Timeout for the request

            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    img_file.write(response.content)
                print(f"Image {filename} downloaded successfully.")
                return True
            else:
                print(f"Failed to retrieve the image {filename}. Status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Error downloading {filename}: {e}")
            return False
    else:
        print(f"Image {filename} already exists. Skipping download.")
        return False

# Use ThreadPoolExecutor to download images concurrently
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(download_image, file) for file in data]
    for future in as_completed(futures):
        future.result()  # We call result to re-raise any exceptions caught during the thread execution
