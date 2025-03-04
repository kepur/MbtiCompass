from sqlalchemy.orm import DeclarativeBase
from .user_model import *
from .post_model import *
from .chat_model import *
from .events_model import *
from .location_model import *
from .payment_model import *

class Base(DeclarativeBase):
    pass
