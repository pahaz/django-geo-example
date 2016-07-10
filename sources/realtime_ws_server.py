import json
import logging
from collections import defaultdict
import asyncio
from asyncio import ensure_future
from datetime import datetime

import aioredis
from aiohttp import web, log

from utils.django import import_django_settings

settings = import_django_settings()


async def index(request):
    return web.Response(body=b"Realtime, hello!")


async def _async_channel_reader(channel_waiters, channel_name, channel):
    log.server_logger.info('start _async_channel_reader for %s', channel_name)
    while await channel.wait_message():
        msg = await channel.get(encoding='utf-8')
        assert json.loads(msg, encoding='utf-8')
        log.server_logger.info("message in %s: %r", channel_name, msg)
        channel_waiters.broadcast(msg)


async def websocket_handler(request):
    channel = request.match_info.get('channel')
    uuid = request.match_info.get('uuid')

    channel_uuids = 'channels:{}:uuids'.format(channel)
    channel_key = 'channels:{}'.format(channel)
    channel_waiters = request.app['waiters'][channel]
    tasks = request.app['tasks']
    is_new_channel = channel not in request.app['channels']

    log.ws_logger.info('handle uuid=%s channel=%s new=%r', uuid, channel,
                       is_new_channel)

    r = request.app['redis']
    sub = request.app['redis_sub']

    async def broadcast(msg, uuid=None):
        try:
            data = json.loads(msg)
        except ValueError:
            raise ValueError('bad message #1')

        if not isinstance(data, dict):
            raise ValueError('bad message #2')

        data['uuid'] = uuid
        data['time'] = datetime.now().strftime('%H:%M:%S %Y-%m-%d')
        data_json = json.dumps(data)

        await r.publish(channel, data_json)
        await r.rpush(channel_key, data_json)
        await r.ltrim(channel_key, -25, -1)

    ws = web.WebSocketResponse(autoclose=False)
    await ws.prepare(request)

    if is_new_channel:
        log.ws_logger.info('open new channel: %s', channel)
        ch1, = await sub.subscribe(channel)
        tsk1 = ensure_future(
            _async_channel_reader(channel_waiters, channel, ch1),
            loop=request.app.loop)
        tasks.append(tsk1)
        request.app['channels'].add(channel)

    channel_waiters.append(ws)
    try:
        count = int(await r.zcard(channel_uuids))
        await r.zadd(channel_uuids, count + 1, uuid)
        users = await r.zrange(channel_uuids)
        await broadcast(json.dumps({'uuids': users}))

        async for msg in ws:
            log.ws_logger.info('%s', msg)

            if msg.tp == web.MsgType.text:
                await broadcast(msg.data, uuid=uuid)
            elif msg.tp == web.MsgType.error:
                log.ws_logger.error('connection closed with exception %r',
                                    ws.exception())
    finally:
        # 2. Send message to all who remained at the channel with new user list
        if ws in channel_waiters:
            channel_waiters.remove(ws)
            await ws.close()
            log.ws_logger.info('Is WebSocket closed?: %r', ws.closed)

        await r.zrem(channel_uuids, uuid)
        users = await r.zrange(channel_uuids)
        broadcast(json.dumps({'uuids': users}))

    return ws


class BList(list):
    """
    [Broadcasting]list that broadcasts str messages for its embers.
    Exclusively for aiohttp WebSocketResponse instances.
    """

    def broadcast(self, message):
        log.ws_logger.info('Sending message to %d waiters', len(self))
        for waiter in self:
            try:
                waiter.send_str(message)
            except Exception:
                log.ws_logger.error('Error was happened during broadcasting: ',
                                    exc_info=True)


async def get_app(loop=None):
    # Graceful shutdown actions

    async def close_redis(app):
        log.server_logger.info('Closing redis')
        app['redis'].close()
        app['redis_sub'].close()
        for task in app['tasks']:
            task.cancel()

    async def close_websockets(app):
        for channel in app['waiters'].values():
            while channel:
                ws = channel.pop()
                await ws.close(code=1000, message='Server shutdown')

    app = web.Application()

    router = app.router
    router.add_route('GET', '/', index)
    router.add_route('GET', '/realtime/{uuid}/{channel}/', websocket_handler)

    app['redis'] = await aioredis.create_redis(
        (settings.REDIS_HOST, 6379), db=1, encoding='utf-8', loop=loop)
    app['redis_sub'] = await aioredis.create_redis(
        (settings.REDIS_HOST, 6379), db=1, encoding='utf-8', loop=loop)
    app['waiters'] = defaultdict(BList)
    app['channels'] = set()
    app['tasks'] = []

    app.on_shutdown.append(close_websockets)
    app.on_cleanup.append(close_redis)

    return app


if __name__ == '__main__':
    debug = settings.DEBUG
    if debug:
        logging.basicConfig(level='DEBUG')
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(get_app(loop=loop))
    web.run_app(app, host='0.0.0.0', port=9999)
