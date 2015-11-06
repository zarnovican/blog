#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Braňo Žarnovičan'
SITENAME = u'Braňo Žarnovičan\'s blog'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Prague'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (
    ('zarnovican@github', 'http://github.com/zarnovican'),
    ('zarnovican@linkedin', 'http://cz.linkedin.com/in/zarnovican'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = '/home/zarnovic/git/pelican-themes/tuxlite_tbs'

