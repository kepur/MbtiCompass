from sqlalchemy.orm import DeclarativeBase
from .user_model import *
from .post_model import *
from .chat_model import *
from .events_model import *
from .location_model import *
from .payment_model import *
from .comment_model import *
from .callsession_model import *
from .m2m_associations_model import *
from .match_model import *

class Base(DeclarativeBase):
    pass
