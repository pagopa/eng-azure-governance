class ApplicationError(RuntimeError):
    """A stable application boundary failure before publication."""

    def __init__(self, message: str, diagnostics=()) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__(message)


class PlatformCoverageError(ApplicationError):
    def __init__(self, diagnostics) -> None:
        self.diagnostics = tuple(diagnostics)
        count = len(self.diagnostics)
        super().__init__(
            f"platform_mapping_unmapped_subscription: {count} unmapped subscription(s); "
            "publication not changed",
            self.diagnostics,
        )


class ContractValidationError(ApplicationError):
    def __init__(self, diagnostics, message: str) -> None:
        self.diagnostics = tuple(diagnostics)
        code = self.diagnostics[0].code if self.diagnostics else "unknown"
        super().__init__(f"{message}: {code}", self.diagnostics)
