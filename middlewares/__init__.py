from aiogram import Dispatcher
from middlewares.spamCM import ThrottlingMiddleware

def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())