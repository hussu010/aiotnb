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


Keypair  Management
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: Keypair

.. autoclass:: Keypair()
    :members:


Verify a Keypair
*****************

Check if a keypair is valid

.. autofunction:: is_valid_keypair

Key From Bytes
***************

Sometimes you may want to convert a key to a nice, readable string.

Keys can be a few different types, and aiotnb includes a type alias to refer to all of them.

.. _anypubkey:

.. important::
    ``AnyPubKey`` is an alias for Union[:class:`nacl.signing.VerifyKey`, :class:`bytes`, :class:`str`]

.. autofunction:: key_as_str


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



Account
~~~~~~~~

.. attributetable:: Account

.. autoclass:: Account()
    :members:

Bank Transaction
~~~~~~~~~~~~~~~~~

.. attributetable:: BankTransaction

.. autoclass:: BankTransaction()
    :members:

Block
~~~~~~

.. attributetable:: Block

.. autoclass:: Block()
    :members:

Confirmation Block
~~~~~~~~~~~~~~~~~~~

.. attributetable:: ConfirmationBlock

.. autoclass:: ConfirmationBlock()
    :members:

Invalid Block
~~~~~~~~~~~~~~

.. attributetable:: InvalidBlock

.. autoclass:: InvalidBlock()
    :members:

Async Iterator
--------------------

Some API endpoints return data in a series of pages marked by offsets. To make using these easier, aiotnb includes an async iterator that automatically fetches new pages as needed.

.. class:: AsyncIterator



    .. admonition:: Supported Operations

        .. describe:: async for x in y

            Asynchronously iterate over the iterator's contents.

    .. method:: next()
        :async:

        |coro|

        Attempts to advanced the iterator by one element.
        Raises :exc:`IteratorEmpty` when no more elements can be found.

    .. method:: find(predicate)
        :async:

        |coro|

        Returns the first item in the iterator that satisfies ``predicate``.

        :param predicate: The predicate (check function) to use. Can be a coroutine.
        :return: The first element that returns ``True`` for the predicate, or ``None`` if none do.

    .. method:: flatten()
        :async:

        |coro|

        Collects the iterator into a single :class:`list`.

        :return: A list of every element.
        :rtype: list

    .. method:: map(func)

        Does basically the same thing as the builtin map, but returns another async iterator with ``func`` applied to every element. The function can be a regular function or a coroutine.

        :param func: Function to call on every element in the iterator
        :rtype: AsyncIterator

    .. method:: filter(predicate)

        Also does basically the same thing as the builtin filter, and returns another async iterator yielding every element that satisfies ``predicate``. This function can also be a coroutine.

        :param predicate: Check function to apply to every element.
        :rtype: AsyncIterator




Enumerations
-------------

.. autoclass:: AccountOrder()
    :members:

.. autoclass:: TransactionOrder()
    :members:

.. autoclass:: BankOrder()
    :members:

.. autoclass:: BlockOrder()
    :members:

.. autoclass:: ConfirmationBlockOrder()
    :members:

.. autoclass:: InvalidBlockOrder()
    :members:

.. autoclass:: UrlProtocol()
    :members:
    
.. autoclass:: NodeType()
    :members:
    
.. autoclass:: CleanCommand()
    :members:
    
.. autoclass:: CleanStatus()
    :members:

.. autoclass:: CrawlCommand()
    :members:

.. autoclass:: CrawlStatus()
    :members:
    



Exceptions
-----------

The following is a list of possible exceptions thrown by aiotnb.

.. autoexception:: TNBException

.. autoexception:: HTTPException
    :members:

.. autoexception:: Unauthorized

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
                - :exc:`Unauthorized`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`NetworkServerError`
            - :exc:`ValidatorException`
            - :exc:`KeysignException`
                - :exc:`KeyfileNotFound`
                - :exc:`SigningKeyLoadFailed`
                - :exc:`VerifyKeyLoadFailed`
                - :exc:`SignatureVerifyFailed`