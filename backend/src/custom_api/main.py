# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
import threading

# internal API imports
import account
import stock
import order
import news
import ranking
import notify
import friends
import quiz
import price_generator

# Get the Flask app from account module
app = account.app


def start_price_generator_once():
    if getattr(app, "_price_generator_started", False):
        return

    app._price_generator_started = True
    thread = threading.Thread(target=price_generator.run, daemon=True)
    thread.start()

# Initialize database tables on first run
@app.before_request
def init_db():
    if not hasattr(app, '_db_initialized'):
        account.Base.metadata.create_all(account.engine)
        app._db_initialized = True
    start_price_generator_once()

if __name__ == '__main__':
    # Initialize database
    account.Base.metadata.create_all(account.engine)
    # Run the Flask app
    app.run(debug=True, port=5000)
