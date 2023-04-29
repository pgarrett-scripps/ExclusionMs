from setuptools import setup
from exclusionms.__version__ import __version__

setup(
    name='exclusionms',
    version=__version__,
    packages=['exclusionms'],
    url='',
    license='',
    author='Patrick Garrett',
    author_email='pgarrett@scripps.edu',
    description='Python package for working with exclusionms-api and exclusionms-streamlit',
    install_requires=['intervaltree==3.1.0',
                      'requests==2.28.2',
                      'pydantic==1.10.4',
                      'ujson==5.7.0',
                      'setuptools==66.1.1',
                      'matplotlib ==3.7.1',
                      'numpy==1.24.1'
                      ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'stress_tester = exclusionms.stress_tester:main'
        ]
    }
)
