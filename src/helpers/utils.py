import os

from src.models.file import FileModel


def calculate_file_size(files: list[FileModel]) -> int | float:
    sum = 0
    for file in files:
        sum += os.path.getsize(file.path)

    return sum
