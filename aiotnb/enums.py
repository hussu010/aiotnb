"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = (
    "AccountOrder",
    "TransactionOrder",
    "BankOrder",
    "BlockOrder",
    "ConfirmationBlockOrder",
    "InvalidBlockOrder",
    "UrlProtocol",
    "NodeType",
    "CleanCommand",
    "CleanStatus",
    "CrawlCommand",
    "CrawlStatus",
)

import logging
from enum import Enum

_log = logging.getLogger(__name__)

# Ordering enums


class AccountOrder(Enum):
    """
    Controls result ordering for an account list request.
    """

    #: Sort accounts by created date.
    created = "created_date"
    #: Sort accounts by created date, descending.
    created_desc = "-created_date"
    #: Sort accounts by modified date.
    modified = "modified_date"
    #: Sort accounts by modified date, descending.
    modified_desc = "-modified_date"
    #: Sort accounts by account ID.
    id = "id"
    #: Sort accounts by account ID, descending.
    id_desc = "-id"
    #: Sort accounts by account number.
    number = "account_number"
    #: Sort accounts by account_number, descending.
    number_desc = "-account_number"
    #: Sort accounts by trust.
    trust = "trust"
    #: Sort accounts by trust, descending.
    trust_desc = "-trust"


class TransactionOrder(Enum):
    """
    Controls result ordering for a transaction list request.
    """

    #: Sort transactions by amount.
    amount = "amount"
    #: Sort transactions by amount, descending.
    amount_desc = "-amount"
    #: Sort transactions by block created date.
    block_created = "block__created_date"
    #: Sort transactions by block created date, descending.
    block_created_desc = "-block__created_date"
    #: Sort transactions by block modified date.
    block_modified = "block__modified_date"
    #: Sort transactions by block modified date, descending.
    block_modified_desc = "-block__modified_date"
    #: Sort transactions by block ID.
    block_id = "block__id"
    #: Sort transactions by block ID, descending.
    block_id_desc = "-block__id"
    #: Sort transactions by block sender.
    block_sender = "block__sender"
    #: Sort transactions by block sender, descending.
    block_sender_desc = "-block__sender"
    #: Sort transactions by ID.
    id = "id"
    #: Sort transactions by ID, descending.
    id_desc = "-id"
    #: Sort transactions by recipient.
    recipient = "recipient"
    #: Sort transactions by recipient, descending.
    recipient_desc = "-recipient"


class BankOrder(Enum):
    """
    Controls result ordering for a bank list request.
    """

    #: Sort banks by ID.
    id = "id"
    #: Sort banks by ID, descending.
    id_desc = "-id"
    #: Sort banks by account number.
    account_number = "account_number"
    #: Sort banks by account number, descending.
    account_number_desc = "-account_number"
    #: Sort banks by IP address.
    ip_address = "ip_address"
    #: Sort banks by IP address, descending.
    ip_address_desc = "-ip_address"
    #: Sort banks by node identifier.
    node_identifier = "node_identifier"
    #: Sort banks by node identifier, descending.
    node_identifier_desc = "-node_identifier"
    #: Sort banks by port.
    port = "port"
    #: Sort banks by port, descending.
    port_desc = "-port"
    #: Sort banks by URL protocol.
    protocol = "protocol"
    #: Sort banks by URL protocol, descending.
    protocol_desc = "-protocol"
    #: Sort banks by version.
    version = "version"
    #: Sort banks by version, descending.
    version_desc = "-version"
    #: Sort banks by TX fee.
    default_transaction_fee = "default_transaction_fee"
    #: Sort banks by TX fee, descending.
    default_transaction_fee_desc = "-default_transaction_fee"
    #: Sort banks by trust.
    trust = "trust"
    #: Sort banks by trust, descending.
    trust_desc = "-trust"


class BlockOrder(Enum):
    """
    Controls result ordering for a block list request.
    """

    #: Sort blocks by created date.
    created = "created_date"
    #: Sort blocks by created date, descending.
    created_desc = "-created_date"
    #: Sort blocks by modified date
    modified = "modified_date"
    #: Sort blocks by modified date, descending.
    modified_desc = "-modified_date"
    #: Sort blocks by ID.
    id = "id"
    #: Sort blocks by ID, descending.
    id_desc = "-id"
    #: Sort blocks by balance key.
    balance_key = "balance_key"
    #: Sort blocks by balance key, descending.
    balance_key_desc = "-balance_key"
    #: Sort blocks by sender.
    sender = "sender"
    #: Sort blocks by sender, descending.
    sender_desc = "-sender"
    #: Sort blocks by signature.
    signature = "signature"
    #: Sort blocks by signature, descending.
    signature_desc = "-signature"


class ConfirmationBlockOrder(Enum):
    """
    Controls result ordering for a confirmation block list request.
    """

    #: Sort confirmation blocks by created date.
    created = "created_date"
    #: Sort confirmation blocks by created date, descending.
    created_desc = "-created_date"
    #: Sort confirmation blocks by modified date.
    modified = "modified_date"
    #: Sort confirmation blocks by modified date, descending.
    modified_desc = "-modified_date"
    #: Sort confirmation blocks by ID.
    id = "id"
    #: Sort confirmation blocks by ID, descending.
    id_desc = "-id"
    #: Sort confirmation blocks by original block ID.
    block = "block"
    #: Sort confirmation blocks by original block ID, descending.
    block_desc = "-block"
    #: Sort confirmation blocks by validator.
    validator = "validator"
    #: Sort confirmation blocks by validator, descending.
    validator_desc = "-validator"
    #: Sort confirmation blocks by block ID.
    block_identifier = "block_identifier"
    #: Sort confirmation blocks by block ID, descending.
    block_identifier_desc = "-block_identifier"


class InvalidBlockOrder(Enum):
    """
    Controls result ordering for an invalid block list request.
    """

    #: Sort blocks by created date.
    created = "created_date"
    #: Sort blocks by created date, descending.
    created_desc = "-created_date"
    #: Sort blocks by modified date.
    modified = "modified_date"
    #: Sort blocks by modified date, descending.
    modified_desc = "-modified_date"
    #: Sort blocks by ID.
    id = "id"
    #: Sort blocks by ID, descending.
    id_desc = "-id"
    #: Sort blocks by original block ID.
    block = "block"
    #: Sort blocks by original block ID, descending.
    block_desc = "-block"
    #: Sort blocks by CV.
    confirmation_validator = "confirmation_validator"
    #: Sort blocks by CV, descending.
    confirmation_validator_desc = "-confirmation_validator"
    #: Sort blocks by PV.
    primary_validator = "primary_validator"
    #: Sort blocks by PV, descending.
    primary_validator_desc = "-primary_validator"
    #: Sort blocks by block ID.
    block_identifier = "block_identifier"
    #: Sort blocks by block ID, descending.
    block_identifier_desc = "-block_identifier"


class UrlProtocol(Enum):
    """
    Specifies a URL scheme to use for a connection.
    """

    #: Use regular HTTP.
    http = "http"
    #: Use secure HTTPS.
    https = "https"


class NodeType(Enum):
    """
    Indicates the role of a specific node.
    """

    #: Indicates a Bank node.
    bank = "BANK"
    #: Indicates a Validator node acting as a Primary validator.
    primary_validator = "PRIMARY_VALIDATOR"
    #: Indicates a Validator node acting as a Confirmation validator.
    confirmation_validator = "CONFIRMATION_VALIDATOR"
    _none = ""


class CleanCommand(Enum):
    """
    Specifies a command to send to a clean endpoint.
    """

    #: Start cleaning.
    start = "start"
    #: Stop cleaning.
    stop = "stop"


class CleanStatus(Enum):  # TODO: figure out possible responses
    """
    Represents the status of a node clean.
    """

    #: Node is currently cleaning.
    active = "cleaning"


class CrawlCommand(Enum):
    """
    Specifies a command to send to a crawl endpoint.
    """

    #: Start crawling.
    start = "start"
    #: Stop crawling.
    stop = "stop"


class CrawlStatus(Enum):  # TODO: figure out possible responses
    """
    Represents the status of a node crawl.
    """

    #: Node is currently crawling.
    active = "crawling"
