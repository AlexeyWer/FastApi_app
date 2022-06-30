from datetime import datetime
from typing import List

from databases.backends.postgres import Record
from sqlalchemy.sql import desc

from app.db import inbox, database


async def create_file(
    request_code: int,
    file_name: str,
    date_created: datetime
) -> int:
    query = inbox.insert().values(
        request_code=request_code,
        file_name=file_name,
        date_created=date_created
    )
    return await database.execute(query=query)


async def get_images_info(request_code: int) -> List[Record]:
    query = inbox.select().where(request_code == inbox.c.request_code)
    return await database.fetch_all(query)


async def delete_image(id: int) -> int:
    query = inbox.delete().where(id == inbox.c.id)
    return await database.execute(query=query)


async def request_code_exsist(request_code: int) -> bool:
    query = (
        inbox.select()
        .where(request_code == inbox.c.request_code)
        .as_scalar()
    )
    result = await database.fetch_one(query)
    if result is not None:
        return True
    return False


async def get_request_code() -> int:
    query = inbox.select().order_by(desc('request_code')).as_scalar()
    last_request_code = await database.fetch_one(query)
    if last_request_code is not None:
        return dict(last_request_code.items())['request_code'] + 1
    return 1
