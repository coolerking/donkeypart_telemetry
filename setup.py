from setuptools import setup

setup(
    name = 'donkeypart_telemetry',
    version = '1.0.0',
    author = 'Tasuku Hori',
    author_email = 'tasuku-hori@exa-corp.co.jp',
    url = 'https://github.com/coolerking/donkeypart_telemetry',
    install_requires = ['donkeycar'],
    extras_require={
        'iotf': ['ibmiotf', 'pytz', 'numpy'],
        'mosq': ['paho-mqtt', 'yaml']
    }
)