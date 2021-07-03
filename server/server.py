import asyncio
import datetime
import logging
import os
import random

import aiofiles
from aiohttp import web

from archive import archive_file

UPTIME_INTERVAL_SECS = 1
DOWNLOAD_BYTES_PER_ITER = 100 * 1024

DEBUG = os.getenv('DEBUG', '').lower() == 'true'
DEBUG_ZIP = os.getenv('DEBUG_ZIP', '').lower() == 'true'


async def archive_download_view(request):
    archive_hash = request.match_info.get('archive_hash')

    try:
        proc = await archive_file(archive_hash)
    except OSError:
        raise web.HTTPNotFound(
            text=f'Архив {archive_hash} не существует или был удален',
        )

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; filename="archive.zip"'
    await response.prepare(request)

    try:
        while not proc.stdout.at_eof():
            logging.debug('Sending archive chunk ...')
            value = await proc.stdout.read(DOWNLOAD_BYTES_PER_ITER)
            await response.write(value)

            if DEBUG_ZIP:
                await asyncio.sleep(random.randint(2, 5))
    except asyncio.CancelledError as e:
        logging.debug('Download was interrupted')
        proc.kill()
        raise e
    except Exception as e:
        logging.debug('Download exception', e)
        proc.kill()
        raise e
    except BaseException as e:
        logging.debug('Download system exception', e)
        proc.kill()
        raise e
    finally:
        logging.debug('Response')
        return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def uptime_handler(request):
    response = web.StreamResponse()

    response.headers['Content-Type'] = 'text/html'

    await response.prepare(request)

    while True:
        formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{formatted_date}<br>'  # <br> — HTML тег переноса строки

        await response.write(message.encode('utf-8'))

        await asyncio.sleep(UPTIME_INTERVAL_SECS)


if __name__ == '__main__':
    app = web.Application()

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)

    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive_download_view),
        web.get('/uptime', uptime_handler),
    ])

    web.run_app(app)
