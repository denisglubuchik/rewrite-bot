from aiogram import Router


def get_handlers_router() -> Router:
    from . import start, main_handlers

    router = Router()
    router.include_routers(
        main.router,
        start.router,
    )

    return router