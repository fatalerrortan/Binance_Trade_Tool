from aiohttp import web
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

@routes.get('/stop')
async def stop(request):
    app_close()
    return web.Response(text="[app] app is stopping!!!")
    

app = web.Application()
app.add_routes(routes)
web.run_app(app)