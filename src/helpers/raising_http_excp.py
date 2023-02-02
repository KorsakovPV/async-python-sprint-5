from fastapi import HTTPException
from starlette import status

from config.constants import APIAnswers


class RaiseHttpException:

    @staticmethod
    def check_is_exist(item):
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=APIAnswers.NOT_FOUND
            )

    @staticmethod
    def check_is_delete(item):
        if item.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail=APIAnswers.GONE
            )

    @staticmethod
    def check_params_isnt_none(**kwargs):
        if all(value is None for value in kwargs.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=APIAnswers.ONE_PARAM
            )

    @staticmethod
    def check_is_one(item):
        if isinstance(item, list) and len(item) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=APIAnswers.MANY_MATCHES
            )
