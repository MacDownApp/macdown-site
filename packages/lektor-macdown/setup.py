from setuptools import setup

setup(
    name='lektor-macdown',
    version='0.1',
    py_modules=['lektor_macdown'],
    installs_requires=['six'],
    entry_points={
        'lektor.plugins': [
            'macdown = lektor_macdown:MacDownPlugin',
        ],
    },
    zip_safe=False,
)
