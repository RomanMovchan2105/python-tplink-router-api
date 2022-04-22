import os

config = {}

CONFIG_FROM_ENV_VARS = {
    'router.ip': 'ROUTER_IP',
    'authorization.basic': 'AUTHORIZATION_BASIC',
}

def initConfig():
    for option in CONFIG_FROM_ENV_VARS:
        from_env = os.environ.get(CONFIG_FROM_ENV_VARS[option], None)
        if from_env:
            config[option] = from_env
