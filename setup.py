# setup.py
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='mipqctool',
    version='0.0.3',
    author='Iosif Spartalis',
    author_email='iosifspart@gmail.com',
    description='A tool for profiling tabular data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aueb-wim/DataQualityControlTool',
    lisence='Apache 2.0',
    keywords='qualitycontrol dataprofiler miplocal',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=['pandas','pylatex'],
    entry_points = {
        'console_scripts': [
            'qctool = mipqctool.__main__:main'
            ]
    },
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache 2.0',
        'Operating System :: OS Independent',
    ),
)
