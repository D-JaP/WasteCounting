from PIL import Image
import pillow_heif
import os
import argparse

parser = argparse.ArgumentParser(description='heic2jpg')

parser.add_argument('img_folder', metavar='HEIC2JPG',
                    help='path to img_folder json')
global arg
arg = parser.parse_args()

def heic_to_jpg(heic_path, jpg_path):
    heif_file = pillow_heif.read_heif(heic_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(jpg_path, "JPEG")

def convert_heic_folder_to_jpg(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".heic"):
                heic_path = os.path.join(root, file)
                jpg_path = os.path.splitext(heic_path)[0] + ".jpg"
                heic_to_jpg(heic_path, jpg_path)
                print(f"Converted: {heic_path} -> {jpg_path}")

def delete_heic_files(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("Folder does not exist.")
        return

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".heic"):
                heic_path = os.path.join(root, file)
                os.remove(heic_path)
                print(f"Deleted: {heic_path}")

if __name__ == "__main__":
    folder_path = arg.img_folder  # Replace with the path to your folder containing HEIC files
    convert_heic_folder_to_jpg(folder_path)
    delete_heic_files(folder_path)


