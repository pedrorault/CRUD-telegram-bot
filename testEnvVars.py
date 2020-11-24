import os

envVars = ['BD2020TOKEN',
    'HOST',
    'DBNAME',
    'USER',
    'PORT',
    'PWBD']

for env in envVars:
    print(os.getenv(env), type(os.getenv(env)))