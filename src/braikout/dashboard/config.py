""" Configuration """
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

PUSHER_APP_ID = '499765'
PUSHER_API_KEY = 'de504dc5763aeef9ff52'
PUSHER_SECRET_KEY = '67dfed0dacf181e74c5d'
PUSHER_CLUSTER = 'eu'
PUSHER_SSL = True

PUSHER_APP_KEY = '36156007aa1b940ca849'
