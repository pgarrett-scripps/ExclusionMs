from pathlib import Path

from setuptools import setup

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

req = 'requirements.txt'
if Path(req).is_file():
    with open(req) as f:
        requirements = f.read().splitlines()
else:
    requirements = []

setup(
    name='exclusionms',
    version='0.1.0',
    packages=['exclusionms'],
    url='',
    license='',
    author='Patrick Garrett',
    author_email='pgarrett@scripps.edu',
    description=long_description,
    install_requires=requirements,
    python_requires='>=3.6'
)
