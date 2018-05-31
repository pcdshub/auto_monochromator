===============================
auto_monochromator
===============================

Toolset for automated mochromator tuning.

Usage (Beta)
------------

An example of this program can be invoked by running the bokeh_monitor command
after installation. This script compares `BLD:SYS0:500:PHOTONENERGY` and
`XPP:SB2:IPM01:SUM`

.. code-block::

  usage: bokeh_monitor [-h] [-p PORT] [-b BINS] [-l LOWER_LIMIT]
                       [-u UPPER_LIMIT] [-o]
  
  Example usage of the real-time histogram features
  
  optional arguments:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  Port to create server on
    -b BINS, --bins BINS  Specify the width of the bins for the histograms
    -l LOWER_LIMIT, --lower_limit LOWER_LIMIT
                          The lower limit of the range for the histogram
    -u UPPER_LIMIT, --upper_limit UPPER_LIMIT
                          The upper limit of the range for the histogram
    -o, --open            Allow server to be reached from other machines by IP address


To launch the server from python, import and run the `launch_server` function found in the
`automonochromator.bokeh_monitor`. An example of this function's usage can be
found in `bin/bokeh_monitor`, the source for the `bokeh_monitor` script
described above.

Note: The current event builder implementation relies on matched events having
precisely the same time stamp. Events without matches will be filtered out. 




Requirements
------------

Python>=3.6

General:
Bokeh
Numpy
Pandas

SLAC Specific:
pcdsdevices


Installation
------------


Running the Tests
-----------------
::

  $ python run_tests.py
   
Directory Structure
-------------------

This repo is based the PCDS python cookiecutter. See the following github page for more info:

- `cookiecutter-pcds-python <https://github.com/pcdshub/cookiecutter-pcds-python>`_
 
