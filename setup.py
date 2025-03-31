from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "StructureTools", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.StructureTools',
      version=str(__version__),
      packages=['freecad',
                'freecad.StructureTools'],
      maintainer="Maykow Menezes",
      maintainer_email="eng.maykowmenezes@gmail.com",
      url="https://www.patreon.com/c/StructureTools",
      description="Workbench for 2d and 3d structural analysis",
      install_requires=['numpy','scipy','prettytable','PyniteFEA[all]'],
      include_package_data=True)
