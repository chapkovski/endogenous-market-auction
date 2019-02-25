from os import environ

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

POINTS_DECIMAL_PLACES = 2
SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 1.00,
    'participation_fee': 0.00,
    'doc': "",
}

SESSION_CONFIGS = [
    {
       'name': 'volauction',
       'display_name': "Endogenous market formation",
       'num_demo_participants': 3,
       'app_sequence': ['volauction'],
        'num_buyers': 2,
        'num_sellers': 1,
        'use_browser_bots': False,
    },
    {
        'name': 'vol_3_4',
        'display_name': "Endogenous market formation, 3 buyers, 4 sellers",
        'num_demo_participants': 7,
        'app_sequence': ['volauction'],
        'num_buyers': 3,
        'num_sellers': 4,
        'use_browser_bots': False,
    },
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '((!26dsfic$(z8v!hxpdj%4@n(v9_n59@v1zf4ym-ol7((x!t4'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
