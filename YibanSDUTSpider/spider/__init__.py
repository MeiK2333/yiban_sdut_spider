# coding=utf-8
import os

from .cookies_cache import SDUT, create_db, db_name, get_user_list
from .dormitory import Dormitory
from .ecard import Ecard
from .edu_manage import EduManage
from .ehall import Ehall
from .lib import Lib
from .logistics import Logistics
from .meol import Meol

if not os.path.exists(db_name):
    create_db()
