from models import FileModel
from schemas.file import FileCreate, FileUpdate
from services.crud import RepositoryDB


class RepositoryFile(RepositoryDB[FileModel, FileCreate, FileUpdate]):
    pass


file_crud = RepositoryFile(FileModel)
