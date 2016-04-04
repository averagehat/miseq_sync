from setuptools import setup, find_packages
from glob import glob

setup(
    name = "redsample",
    version = "0.0.1",
    packages = find_packages(),
    author = "Tyghe Vallard",
    author_email = "vallardt@gmail.com",
    description = "Tasks related to redmine samples",
    license = "PSF",
    keywords = "",
    scripts = glob('bin/*'),
    install_requires = ['python-redmine'],
    setup_requires = ['nose'],
    tests_require = ['nose','mock'],
)
