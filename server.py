from math import trunc
from aiohttp import web
import aiohttp
import asyncio
from aiofile import async_open
from app import trading, app_close
from App_Logging import getLogger
import threading
import os
# from multiprocessing import Process

logger = getLogger('server.py')
x = None
exit_event = threading.Event()
th_id = None

routes = web.RouteTableDef()

@routes.post('/app')
async def run(request):

    global x
    os.environ["__exit__"] = "no"

    data = await request.post()
    logger.info("[app] app is launching!!!") 
    x = threading.Thread(target=thread, args=(data,))
    # x = Process(target=thread, args=(data,))
    x.start()    
    # await trading(data)
    return web.Response(text="[app] app is launching!!!")

def thread(data):
    asyncio.run(trading(data))

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
    os.environ["__exit__"] = "yes"
    # app_close()
    
    return web.Response(text="[app] app is stopping!!!")
     
app = web.Application()
app.add_routes(routes)
web.run_app(app, port = 9898)