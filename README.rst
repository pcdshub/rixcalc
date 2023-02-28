===============================
rixcalc
===============================

.. image:: https://img.shields.io/travis/pcdshub/rixcalc.svg
        :target: https://travis-ci.org/pcdshub/rixcalc

.. image:: https://img.shields.io/pypi/v/rixcalc.svg
        :target: https://pypi.python.org/pypi/rixcalc


This is a caproto based IOC for the purpose of performing python based calculation, and converting the outputs to usable PVs.

Currently, this calculator can find the focus position from MR1K1, MR3K2, MR4K2, with the latter two being from the reference point of chemRIXS. Future renditions of this calculator will likely include separate calculations for finding the focus relative to the IP of the qRIXS experiment. Additionally, the calculator can find the targeted and calcated energy level of the monochromator. Lastly, it can calcualate the reciprocal linear dispersion of the monochromator throught the exit slit plane.

Reciprocal linear dispersion is the spatial separation of wavelengths on the exit focal plane.

Documentation
-------------

Sphinx-generated documentation for this project can be found here:
https://pcdshub.github.io/rixcalc/

Requirements
------------

Describe the project requirements (i.e. Python version, packages and how to install them)

Installation
------------

..

    pip install git+https://github.com/pcdshub/rixcalc


Running the Tests
-----------------
::

  $ pip install -r dev-requirements.txt
  $ pytest -vv
