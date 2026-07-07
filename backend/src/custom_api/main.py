# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

# internal API imports
import account
import stock
import order
import news
import ranking
import notify
import friends
import quiz

# Get the Flask app from account module
app = account.app

# Initialize database tables on first run
@app.before_request
def init_db():
    if not hasattr(app, '_db_initialized'):
        account.Base.metadata.create_all(account.engine)
        app._db_initialized = True

if __name__ == '__main__':
    # Initialize database
    account.Base.metadata.create_all(account.engine)
    # Run the Flask app
    app.run(debug=True, port=5000)
