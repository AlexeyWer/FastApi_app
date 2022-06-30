import os
import uuid
from datetime import datetime
from io import BytesIO
from typing import List

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Response,
    status,
    UploadFile,
)
from minio import Minio

from app.api import crud, models

MINIO_URL = os.getenv('MINIO_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')


minio_client = Minio(
   MINIO_URL,
   access_key=MINIO_ACCESS_KEY,
   secret_key=MINIO_SECRET_KEY,
   secure=False
)

router = APIRouter()


@router.post(
    '/',
    response_model=List[models.InfoFilesOut],
    status_code=status.HTTP_201_CREATED
)
async def create_images(
    files: List[UploadFile] = File(
        ...,
        description='Upload only image of no more than 15 pieces'
    ),
):
    time_now = datetime.now()
    request_code = await crud.get_request_code()
    print(request_code)
    bucket_name = time_now.strftime('%Y%m%d')
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    for file in files[:15]:
        if 'image' not in str(file.content_type):
            continue
        data = file.file.read()
        filename = str(uuid.uuid4()) + '.jpg'
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=BytesIO(data),
            content_type=file.content_type,
            length=-1,
            part_size=10*1024*1024
        )
        print(await crud.create_file(
            request_code=request_code,
            file_name=filename,
            date_created=time_now
        ))
        file.file.close()
    records = await crud.get_images_info(request_code=request_code)
    print(records)
    response = []
    for record in records:
        response.append(models.InfoFilesOut(**record))
    if response == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload only images"
        )
    return response


@router.get(
    '/{request_code}/',
    response_model=List[models.GetImageOut],
    status_code=status.HTTP_200_OK
)
async def get_images(request_code: int):
    if await crud.request_code_exsist(request_code):
        records = await crud.get_images_info(request_code)
        print(records)
        response = []
        for record in records:
            response.append(models.InfoFilesOut(**record))
        return response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'request code <{request_code}> not found'
    )


@router.delete('/{request_code}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_images(request_code: int):
    if await crud.request_code_exsist(request_code):
        records = await crud.get_images_info(request_code)
        bucket_name = datetime.fromisoformat(
           str(records[0]['date_created'])
        ).strftime('%Y%m%d')
        for record in records:
            minio_client.remove_object(bucket_name, record['file_name'])
            await crud.delete_image(record['id'])
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'request code <{request_code}> not found'
    )
