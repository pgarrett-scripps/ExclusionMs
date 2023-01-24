from setuptools import setup

setup(
    name='exclusionms',
    version='0.1.2',
    packages=['exclusionms'],
    url='',
    license='',
    author='Patrick Garrett',
    author_email='pgarrett@scripps.edu',
    description='Python package for working with exclusionms-api and exclusionms-streamlit',
    install_requires=['intervaltree==3.1.0', 'requests==2.28.2', 'pandas==1.5.3', 'setuptools==66.1.1', 'pydantic==1.10.4'],
    python_requires='>=3.6'
)
