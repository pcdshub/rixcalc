import sys
from os import path

import versioneer
from setuptools import find_packages, setup

MIN_VERSION = (3, 6)

if sys.version_info < MIN_VERSION:
    error = """
rixcalc does not support Python {0}.{1}.
Python {2}.{3} and above is required. Check your Python version like so:

python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1.
Upgrade pip like so:

pip install --upgrade pip
""".format(*sys.version_info[:2], *MIN_VERSION)
    sys.exit(error)


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if line and not line.startswith('#')]


setup(
    name='rixcalc',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='SLAC',
    author='SLAC National Accelerator Laboratory',
    packages=find_packages(exclude=['docs', 'tests']),
    description='General Purpose IOC for using python to calculate and build various PVs for RIX hutch',
    long_description=readme,
    url='https://github.com/pcdshub/rixcalc',  # noqa
    entry_points={
        'console_scripts': [
            'rixcalc=rixcalc.__main__:main',  # noqa
            ],
        },
    include_package_data=True,
    package_data={
        'rixcalc': [
            # When adding files here, remember to update MANIFEST.in as well,
            # or else they will not be included in the distribution on PyPI!
            # 'path/to/data_file',
            ]
        },
    install_requires=requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)
