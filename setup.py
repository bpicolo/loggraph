from setuptools import find_packages
from setuptools import setup

setup(
    name='loggraph',
    version='0.0.2',
    author='Ben Picolo',
    author_email='be.picolo@gmail.com',
    url='https://github.com/bpicolo/loggraph',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': ['loggraph=loggraph.main:main']
    },
    install_requires=[
        'bokeh',
        'ciso8601',
        'pandas',
        'python-dateutil',
        'ujson'
    ]
)
