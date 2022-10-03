import os
from os import listdir
from os.path import isfile, join
import time
import re
import warnings
import ftplib

watch_directory = r'c:\cnc_transfer'
poll_time = 5  # in seconds


# function to return files in a directory
def file_in_directory(my_dir: str):
    only_files = [f for f in listdir(my_dir) if isfile(join(my_dir, f))]
    return only_files


# function comparing two lists

def list_comparison(original_list: list, new_list: list):
    differences_list = [x for x in new_list if
                        x not in original_list]  # Note if files get deleted, this will not highlight them
    return differences_list


def do_things_with_new_files(new_files: list):
    print(f'*******  NEW FILES {new_files}  *******')

    # if file fits brother file format send on to cnc and delete
    # O****.NC     https://www.regextester.com/
    # ^[O]\d{4}[.][N][C]$

    pattern = r"^[O]\d{4}[.][N][C]$"

    # TESTS
    # print(re.match(pattern, "O1234.NC"))
    # print(re.match(pattern, "o1234.NC"))
    # print(re.match(pattern, "O12344.NC"))
    # print(re.match(pattern, "OO1234.NC"))
    # print(re.match(pattern, "O1234.NCC"))
    # print(re.match(pattern, "O1234.Nc"))

    for file_name in new_files:
        match = re.match(pattern, file_name)
        print(file_name, match)
        if match is None:
            warning_msg = "Warning: " + file_name + ' is invalid!'
            print(warning_msg)
            warnings.warn(warning_msg)
        else:
            full_path = os.path.join(watch_directory, file_name)
            print(full_path)

            # SEND IT!
            session = ftplib.FTP("192.168.1.50", "BS", "BS")
            file = open(full_path, "rb")
            session.storbinary(f'STOR {file_name}', file)
            file.close()
            session.quit()

            os.remove(full_path)


def file_watcher(my_dir: str, my_poll_time: int):
    print("started watch")

    while True:
        if 'watching' not in locals():  # Check if this is the first time the function has run
            previous_file_list = file_in_directory(my_dir)
            watching = 1

        time.sleep(my_poll_time)

        new_file_list = file_in_directory(my_dir)

        file_diff = list_comparison(previous_file_list, new_file_list)

        previous_file_list = new_file_list
        if len(file_diff) == 0: continue
        do_things_with_new_files(file_diff)


file_watcher(watch_directory, poll_time)
