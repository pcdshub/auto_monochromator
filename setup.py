import versioneer
from setuptools import setup, find_packages

setup(name='auto_monochromator',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      license='BSD',
      author='SLAC National Accelerator Laboratories',
      packages=find_packages(),
      description='Toolset for automated mochromator tuning',
      scripts=['bin/bokeh_monitor'],
      )
