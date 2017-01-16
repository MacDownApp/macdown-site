from setuptools import find_packages, setup

setup(
    name='lektor-macdown',
    version='0.1',
    packages=find_packages(),
    install_requires=['lektor', 'markupsafe', 'six'],
    entry_points={
        'lektor.plugins': [
            'macdown = lektor_macdown:MacDownPlugin',
        ],
    },
    zip_safe=False,
)
