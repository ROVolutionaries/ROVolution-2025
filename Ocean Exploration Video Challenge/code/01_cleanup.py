import json
import os

json_file_path = "data.json"
images_directory = "images/"

"""
Deleting entries without width or height
"""
with open(json_file_path, "r") as file:
    data = json.load(file)

filtered_data = []
deleted_entries = []

for entry in data:
    if 'width' in entry and 'height' in entry:
        filtered_data.append(entry)
    else:
        deleted_entries.append(entry)

with open(json_file_path, "w") as file:
    json.dump(filtered_data, file)

print(f"Updated JSON file saved to {json_file_path}")
if deleted_entries:
    print("\nDeleted entries:")
    for entry in deleted_entries:
        print(entry)
else:
    print("No entries were deleted.")

"""
Finding and removing any extra images or JSON entries
"""
with open(json_file_path, "r") as file:
    data = json.load(file)

json_filenames = {entry["uuid"] + ".png" for entry in data}

image_filenames = {filename for filename in os.listdir(images_directory) if filename.endswith(".png")}

extra_json_entries = json_filenames - image_filenames
extra_image_files = image_filenames - json_filenames

print(f"Extra JSON entries (not having corresponding image files): {len(extra_json_entries)}")
print(f"Extra image files (not referenced in JSON): {len(extra_image_files)}")

for filename in extra_image_files:
    file_path = os.path.join(images_directory, filename)
    try:
        os.remove(file_path)
        print(f"Removed extra image file: {file_path}")
    except OSError as e:
        print(f"Error removing file {file_path}: {e}")

filtered_data = [entry for entry in data if entry["uuid"] + ".png" not in extra_json_entries]

with open(json_file_path, "w") as file:
    json.dump(filtered_data, file)

print("Filtered data saved to JSON file.")
print("Cleanup complete.")


"""
Printing the number of JSON entries
"""
with open(json_file_path, "r") as file:
    data = json.load(file)

file_count_json = len(data)

print(f"Total number of json files {file_count_json}")

"""
Printing the number of images and total size
"""
def get_folder_info(images_directory):
    file_count = 0
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(images_directory):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            total_size += os.path.getsize(file_path)
            file_count += 1

    return file_count, total_size

file_count, total_size = get_folder_info(images_directory)

print(f"Number of files: {file_count}")
print(f"Total size in bytes: {total_size}")
