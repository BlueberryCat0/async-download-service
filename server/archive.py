import asyncio
import os

ARCHIVE_FILES_PATH = os.getenv('ARCHIVE_FILES_PATH', 'test_photos')


async def archive_file(archive_hash):
    path = f'{ARCHIVE_FILES_PATH}/{archive_hash}/'
    if not os.path.exists(path):
        raise OSError(path)

    proc = await asyncio.subprocess.create_subprocess_exec(
        'zip', '-r', '-',
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    return proc
