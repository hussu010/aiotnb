.. currentmodule:: aiotnb

API Reference
==============

This is the entire API of aiotnb.

.. note::
    aiotnb uses the Python logging module for errors and diagnostic information. If not configured, these logs will not be saved. Check :ref:`logging_setup` for information on how to setup and use ``logging`` with aiotnb.

Version Info
-------------

.. data:: version_info

    Similar to :obj:`py:sys.version_info`, but a dataclass instead of a named tuple.

    Fields are the same, and valid values for ``releaselevel`` are the same as well.

.. data:: __version__

    The current version number as a semver-style string, eg. ``'0.1.0b'``.

Core
-----

Connect to a bank
~~~~~~~~~~~~~~~~~~

See the TNB `Bank API <https://thenewboston.com/bank-api/>`_ documentation.

.. autofunction:: connect_to_bank

Connect to a Primary Validator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the TNB `Primary Validator API <https://thenewboston.com/primary-validator-api/>`_ documentation.

.. autofunction:: connect_to_pv


Connect to a Confirmation Validator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the TNB `Confirmation Validator API <https://thenewboston.com/confirmation-validator-api/>`_ documentation.

.. autofunction:: connect_to_cv


Keypair Account Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: LocalAccount

.. autoclass:: LocalAccount
    :members:


Verify a Keypair
~~~~~~~~~~~~~~~~~

Check if a Keypair is valid

.. autofunction:: is_valid_keypair

Exceptions
-----------

    The following is a list of possible exceptions thrown by aiotnb.

    .. autoexception:: TNBException

    .. autoexception:: HTTPException
        :members:

    .. autoexception:: Forbidden

    .. autoexception:: NotFound

    .. autoexception:: NetworkServerError

    .. autoexception:: KeysignException
        :members:

    .. autoexception:: KeyfileNotFound

    .. autoexception:: SigningKeyLoadFailed

    .. autoexception:: VerifyKeyLoadFailed

    .. autoexception:: SignatureVerifyFailed

    .. autoexception:: ValidatorException


Exception Reference
~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`TNBException`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`NetworkServerError`
            - :exc:`ValidatorException`
            - :exc:`KeysignException`
                - :exc:`KeyfileNotFound`
                - :exc:`SigningKeyLoadFailed`
                - :exc:`VerifyKeyLoadFailed`
                - :exc:`SignatureVerifyFailed`
