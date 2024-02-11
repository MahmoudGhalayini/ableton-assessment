# Copyright 2024 Ableton
# All rights reserved


import configparser

config = configparser.ConfigParser()
config.read('.env')


SECRET_KEY = config.get('VARIABLES', 'SECRET_KEY', fallback='your secret key')
AUTH_TOKEN_EXPIRY_PERIOD = config.get('VARIABLES',
                                      'AUTH_TOKEN_EXPIRY_PERIOD_IN_MINS',
                                      fallback=1440)
VERIFICATION_TOKEN_EXPIRY_PERIOD = config.get('VARIABLES',
                                              'VERIFICATION_TOKEN_EXPIRY_PERIOD_IN_MINS',
                                              fallback=1440)
