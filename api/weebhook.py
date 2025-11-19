from aiohttp import web
from main import webhook_handler

async def handle_webhook(request):
    """Обработчик вебхука для Vercel"""
    return await webhook_handler(request)

app = web.Application()
app.router.add_post('/api/webhook', handle_webhook)

if __name__ == '__main__':
    web.run_app(app, port=3000)
