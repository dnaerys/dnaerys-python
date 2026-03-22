"""Channel creation for gRPC connections to the Dnaerys service."""

from __future__ import annotations

from typing import Any

import grpc


def create_channel(
    target: str,
    *,
    tls: bool,
    credentials: grpc.ChannelCredentials | None,
    options: dict[str, Any] | None,
) -> grpc.Channel:
    """Create a gRPC channel to the Dnaerys service.

    Parameters
    ----------
    target : str
        Server address in ``host:port`` format.
    tls : bool
        If ``True``, create a secure channel. If ``False``, insecure.
    credentials : grpc.ChannelCredentials | None
        Custom TLS credentials. If ``None`` and *tls* is ``True``,
        default SSL credentials are used.
    options : dict[str, Any] | None
        gRPC channel options as ``{key: value}`` pairs. Converted to
        a list of ``(key, value)`` tuples for the gRPC channel constructor.

    Returns
    -------
    grpc.Channel
        The created gRPC channel.

    Raises
    ------
    ValueError
        If *credentials* is provided with ``tls=False`` (insecure channels
        cannot use TLS credentials).
    """
    channel_options = list(options.items()) if options else None

    if tls:
        creds = credentials if credentials is not None else grpc.ssl_channel_credentials()
        return grpc.secure_channel(target, creds, options=channel_options)
    else:
        if credentials is not None:
            raise ValueError(
                "credentials cannot be provided when tls=False; "
                "use tls=True for secure channels"
            )
        return grpc.insecure_channel(target, options=channel_options)
