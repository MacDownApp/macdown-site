from setuptools import setup

setup(
    name='lektor-humanize',
    version='0.1',
    py_modules=['lektor_humanize'],
    installs_requires=['lektor'],
    entry_points={
        'lektor.plugins': [
            'humanize = lektor_humanize:HumanizePlugin',
        ],
    },
)
