from setuptools import setup, find_packages

import miseq_sync

setup(
    name = miseq_sync.__projectname__,
    version = miseq_sync.__release__,
    packages = find_packages(),
    author = miseq_sync.__authors__,
    author_email = miseq_sync.__authoremails__,
    description = miseq_sync.__description__,
    license = "GPLv2",
    keywords = miseq_sync.__keywords__,
    entry_points = {
        'console_scripts': [
            'miseq_sync = miseq_sync.miseq_sync:main'
        ],
    },
)
