"""Watchdog KOTH CTFd plugin."""


def load(app):
    from CTFd.plugins import register_admin_plugin_menu_bar

    from .models import create_tables
    from .routes import register_routes

    create_tables()
    register_routes(app)
    register_admin_plugin_menu_bar(
        title="Watchdog KOTH",
        route="/admin/watchdog-koth",
    )
