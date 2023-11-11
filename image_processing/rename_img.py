import os
import argparse

parser = argparse.ArgumentParser(description='heic2jpg')

parser.add_argument('img_folder', metavar='HEIC2JPG',
                    help='rename img start from number')
parser.add_argument('start_from', metavar='int',
                    help='start from num')
global arg
arg = parser.parse_args()



def rename_files_with_incrementing_numbers(folder_path, start_from):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("Folder does not exist.")
        return

    files = os.listdir(folder_path)
    files.sort()  # Sort the files alphabetically

    # Initialize a counter for the numeric names
    count = int(start_from)

    for file in files:
        old_path = os.path.join(folder_path, file)
        if os.path.isfile(old_path):
            # Get the file extension (e.g., .jpg, .txt)
            _, file_extension = os.path.splitext(file)

            # Create the new file name with an incrementing number
            new_file_name = f"{count:03d}{file_extension}"

            new_path = os.path.join(folder_path, new_file_name)

            os.rename(old_path, new_path)
            count += 1

if __name__ == "__main__":
    folder_path = arg.img_folder  # Replace with the path to your folder
    rename_files_with_incrementing_numbers(folder_path, arg.start_from)