.. currentmodule:: aiotnb

API Reference
==============

This is the entire API of aiotnb.

.. seealso::
    aiotnb uses the Python logging module for errors and diagnostic information. If not configured, these logs will not be saved.
    Check :ref:`logging_setup` for information on how to setup and use ``logging`` with aiotnb.

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

See the TNB `Validator API <https://thenewboston.com/primary-validator-api/>`_ documentation.

.. autofunction:: connect_to_validator


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

Check if a keypair is valid

.. autofunction:: is_valid_keypair


Models
-------

Bank
~~~~~

.. attributetable:: Bank

.. autoclass:: Bank()
    :members:

Primary Validator
~~~~~~~~~~~~~~~~~~

.. attributetable:: Validator

.. autoclass:: Validator()
    :members:

Confirmation Validator
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ConfirmationValidator

.. autoclass:: ConfirmationValidator()
    :members:


Common
~~~~~~~

Paginated Responses
********************

Some API endpoints return just one page of possible data. In aiotnb, these methods return an async iterator over the pages of data.

.. attributetable:: PaginatedResponse

.. autoclass:: PaginatedResponse()
    :members:



Account
********

.. attributetable:: Account

.. autoclass:: Account()
    :members:


Enumerations
-------------

.. class:: UrlProtocol
    
    Specifies the URL scheme to use for a given node connection.

    .. attribute:: http

        Use regular HTTP.

    .. attribute:: https

        Use secure HTTPS.


.. class:: NodeType

    Specifies the type of a given node.

    .. attribute:: bank

        Signifies a Bank node.

    .. attribute:: primary_validator

        Signifies a Validator node acting as a PV.

    .. attribute:: confirmation_validator

        Signifies a Validator node acting as a CV.


.. class:: AccountOrder

    Specifies results ordering for an accounts endpoint request.

    .. attribute:: created_asc

        Sort accounts by created dated.

    .. attribute:: created_desc

        Sort accounts by created date, descending.

    .. attribute:: modified_asc

        Sort accounts by modified date.

    .. attribute:: modified_desc

        Sort accounts by modified date, descending.

    .. attribute:: id_asc

        Sort accounts by account ID.

    .. attribute:: id_desc

        Sort accounts by account ID, descending.

    .. attribute:: number_asc

        Sort accounts by account number.

    .. attribute:: number_desc

        Sort accounts by account_number, descending.

    .. attribute:: trust_asc

        Sort accounts by trust.

    .. attribute:: trust_desc

        Sort accounts by trust, descending.




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
    :members:


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