from math import trunc
from aiohttp import web
import aiohttp
import asyncio
from aiofile import async_open
from app import trading, app_close
from App_Logging import getLogger

logger = getLogger('server.py')
routes = web.RouteTableDef()

@routes.post('/app')
async def run(request):
    data = await request.post()
    logger.info("[app] app is launching!!!") 
    await trading(data)
    return web.Response(text="[app] app is launching!!!")

@routes.get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "detach":
                await ws.close()
            if msg.data == "attach":               
                async with async_open("app.log", 'r') as afp:
                    while True:
                        line = await afp.readline()
                        if len(line) == 0: 
                            await asyncio.sleep(15)
                            continue
                        await ws.send_str(line)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('ws connection closed with exception %s' %
                  ws.exception())

    logger.warning('websocket connection closed')

    return ws

@routes.get('/stop')
async def stop(request):
    logger.warning('[app] app is stopping!!!')
    app_close()
    return web.Response(text="[app] app is stopping!!!")
     

app = web.Application()
app.add_routes(routes)
web.run_app(app, port = 9898)

