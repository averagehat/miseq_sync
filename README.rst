miseq_sync
===============
.. image:: https://readthedocs.org/projects/python-template/badge/?version=latest
    :target: http://python-template.readthedocs.org/en/latest/
    :alt: Documentation Status

.. image:: https://travis-ci.org/VDBWRAIR/miseq_sync.svg
    :target: https://travis-ci.org/VDBWRAIR/miseq_sync

.. image:: https://coveralls.io/repos/VDBWRAIR/miseq_sync/badge.svg
    :target: https://coveralls.io/r/VDBWRAIR/miseq_sync


This is the template for WRAIR python projects that will help you quickly setup
a base project that you can easily expand upon.

Features
--------

* .travis.yml to hook in with https://travis-ci.org
* .travis.yml pushes to https://coveralls.io
* sphinx docs directory for your documentation that can be hooked into 
  Read The Docs
* tox.ini to allow you to easily run tests through different python environments
* tests directory stub
* python package directory
* setup.py installation script

How To Use
----------

#. Clone this repo
#. Rename the directory to your project name
#. Modify the git origin remote so it points to your new project's github 
   project
#. Anywhere you see miseq_sync you will need to rename that to your
   project name.
   The following should work to rename all miseq_sync to miseq_sync

    .. code-block:: bash

        find . -path ./.git -prune -o -type f -exec sed -i 's/miseq_sync/miseq_sync/g' {} \;

Travis CI
---------

#. Head over to https://travis-ci.org
#. You should be able to sign up with your github account here.
#. On the left side of the page you will see 'My Repositories', 'Recent' and
   a plus symbol. Click the plus symbol to list all your github repos.
#. Click the 'sync' button to make sure all your github repos are synced such
   that travis can see them
#. Find your project in the list and slide the toggle switch to green

Coveralls IO
------------

#. Head over to https://coveralls.io
#. You should be able to sign up with your github account here.
#. Click Add Repos
#. Click sync github repos
#. Find your project and slide the toggle switch to On

Read The Docs
-------------

#. Head over to https://readthedocs.org
#. Sign up for an account
#. Click import a project
#. Select Import from GitHub
#. Click sync your github projects
#. Find your project and click Create
#. Click Next
