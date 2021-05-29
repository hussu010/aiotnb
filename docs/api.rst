.. currentmodule:: aiotnb

API Reference
==============

This is the entire API of aiotnb.

.. note::
    aiotnb uses the Python logging module for errors and diagnostic information. If not configured, these logs will not be saved. Check :ref:`logging_setup` for information on how to setup and use ``logging`` with aiotnb.

Version Info
-------------

.. data:: __version__

    The current version number as a semver-style string, eg. ``'0.1.0b'``.

Core
-----

Connect to a Bank
~~~~~~~~~~~~~~~~~~

.. autofunction:: connect_to_bank
