#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://zarnovican.github.io'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'

LINKS = (
    ('Atom Feed', '/'+FEED_ALL_ATOM),
    ('RSS Feed', '/'+FEED_ALL_RSS),
)

DELETE_OUTPUT_DIRECTORY = True
OUTPUT_RETENTION = ('.git', )

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""
