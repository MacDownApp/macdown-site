from setuptools import find_packages, setup

setup(
    name='lektor-macdown',
    version='0.1',
    packages=find_packages(),
    installs_requires=[
        'lektor', 'markupsafe', 'pyobjc-framework-webkit', 'six',
    ],
    entry_points={
        'lektor.plugins': [
            'macdown = lektor_macdown:MacDownPlugin',
        ],
    },
    zip_safe=False,
)
