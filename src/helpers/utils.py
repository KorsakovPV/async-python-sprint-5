import os

from models import FileModel


def calculate_file_size(files: list[FileModel]) -> int:
    sum = 0
    for file in files:
        sum += os.path.getsize(file.path)

    return sum
