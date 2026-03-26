from __future__ import annotations


class ProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        transient: bool = False,
        timeout: bool = False,
    ) -> None:
        super().__init__(message)
        self.transient = transient
        self.timeout = timeout
