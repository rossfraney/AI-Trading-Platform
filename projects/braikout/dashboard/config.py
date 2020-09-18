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

PUSHER_APP_ID = ''
PUSHER_API_KEY = ''
PUSHER_SECRET_KEY = ''
PUSHER_CLUSTER = 'eu'
PUSHER_SSL = True

PUSHER_APP_KEY = ''
