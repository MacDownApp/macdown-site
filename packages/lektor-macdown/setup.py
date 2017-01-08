from setuptools import setup

setup(
    name='lektor-macdown',
    version='0.1',
    py_modules=['lektor_macdown'],
    entry_points={
        'lektor.plugins': [
            'macdown = lektor_macdown:MacDownPlugin',
        ]
    },
)
