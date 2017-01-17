from setuptools import setup

setup(
    name='lektor-atom',
    version='0.2+',
    author='A. Jesse Jiryu Davis',
    author_email='jesse@emptysquare.net',
    license='MIT',
    py_modules=['lektor_atom'],
    install_requires=['markupsafe'],
    url='https://github.com/ajdavis/lektor-atom',
    entry_points={
        'lektor.plugins': [
            'atom = lektor_atom:AtomPlugin',
        ]
    }
)
