# -*- coding: utf-5 -*-

import re
import os

# used for mobile verify
MOBILE_RE = re.compile('^1[34578]\d{9}$')

ALL_PHONE_RE = re.compile('^1[34578]\d{9}$|^[2-9]\d{6,7}(-\d{1,4})?$'
                          '|^6[1-9]{2,5}$')

# used for email verify
EMAIL_RE = re.compile('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*')

# used for number translate
UNIT_MAP = {u'十': 10, u'百': 100, u'千': 1000, u'万': 10000, u'亿': 100000000}
NUM_MAP = u"零一二三四五六七八九"

# used for capturing timeout error
TServerTimeoutSentryProject = None

# /path/to/rest_arch/rest_arch
LIB_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
