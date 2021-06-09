"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("Bank", "ConfirmationValidator", "Validator", "UrlProtocol", "NodeType")


from enum import Enum
from typing import TYPE_CHECKING, cast

from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey
from yarl import URL

from .http import HTTPClient, HTTPMethod, Route

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional


class UrlProtocol(Enum):
    """
    A value representing possible URL schemes.
    """

    http = "http"
    https = "https"


class NodeType(Enum):
    """
    A value representing possible node types.
    """

    bank = "BANK"
    primary_validator = "PRIMARY_VALIDATOR"
    confirmation_validator = "CONFIRMATION_VALIDATOR"


class Bank:
    """
    Object representing a Bank node on the TNB network. This object should not be manually created, instead use ``.connect_to_bank``.


    Attributes
    ----------
    account_number: :class:`bytes`
        The account number of the Bank node as hex-encoded bytes.

    node_identifier: :class:`bytes`
        The node identifier (NID) of the Bank node as hex-encoded bytes.

    version: :class:`str`
        The version identifier of the node.

    transaction_fee: :class:`int`
        The fee this node charges for handling transactions.

    node_type: :class:`.NodeType`
        An enum value representing the type of node. Will always be ``NodeType.Bank``.

    ip_address: :class:`str`
        The IP address of this Bank node.

    port: :class:`int`
        The port number this node accepts connections on.

    protocol: :class:`.UrlProtocol`
        An enum value representing the scheme this node handles connections with.

    address: :class:`~yarl.URL`
        The fully-formed URL for this node.

    primary_validator: Mapping[:class:`str`, Any]
        The primary Validator node this Bank node uses. For now this is just the raw response data.

    """

    def __init__(
        self,
        _client: HTTPClient,
        *,
        account_number: VerifyKey,
        ip_address: URL,
        node_identifier: VerifyKey,
        port: Optional[int],
        protocol: UrlProtocol,
        version: str,
        default_transaction_fee: int,
        node_type: NodeType,
        primary_validator: Mapping[str, Any],
    ):
        self.account_number = account_number.encode(encoder=HexEncoder)
        self._account_number = account_number

        self.node_identifier = node_identifier.encode(encoder=HexEncoder)
        self._node_identifier = node_identifier

        self.version = version  # TODO: int-tuple for version
        self.transaction_fee = default_transaction_fee

        self.node_type = node_type
        assert (
            node_type == NodeType.bank
        ), f"attempt to initiate a Bank object with non-bank node data: {node_type.value}"

        self.ip_address = str(ip_address)
        self.port = port
        self.protocol = protocol

        self.address = URL.build(
            scheme=protocol.value,
            host=self.ip_address,
            port=port or 80,
        )

        self.primary_validator = primary_validator

        self._client = _client


class ConfirmationValidator:
    """
    Object representing a Confirmation Validator on the TNB network.

    """

    pass


class Validator:
    """
    Object representing a Validator on the TNB network.

    """

    pass
