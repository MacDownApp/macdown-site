from setuptools import setup

setup(
    name='lektor-humanize',
    version='0.1',
    py_modules=['lektor_humanize'],
    entry_points={
        'lektor.plugins': [
            'humanize = lektor_humanize:HumanizePlugin',
        ],
    },
)
