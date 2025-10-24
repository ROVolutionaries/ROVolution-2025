import json
import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

json_file_path = "data.json"
images_directory = "images/"
smaller_json_file_path = "small_data.json"

# Create images directory if it doesn't exist
os.makedirs(images_directory, exist_ok=True)

# Read the original JSON file
with open(json_file_path, "r") as file:
    data = json.load(file)

# Create a smaller subset of 500 images
subset_size = 500
if len(data) > subset_size:
    data_subset = random.sample(data, subset_size)
else:
    data_subset = data

# Save the smaller subset to a new JSON file
with open(smaller_json_file_path, "w") as small_file:
    json.dump(data_subset, small_file, indent=4)

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

def main(max_workers):
    start_time = time.time()
    # Use ThreadPoolExecutor to download images concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_image, file) for file in data_subset]
        for future in as_completed(futures):
            future.result()  # We call result to re-raise any exceptions caught during the thread execution
    end_time = time.time()
    print(f"Time taken with {max_workers} workers: {end_time - start_time} seconds")

if __name__ == "__main__":
    # Test with different numbers of workers
    for workers in [10, 20, 50, 100]:
        print(f"Testing with {workers} workers")
        main(workers)
