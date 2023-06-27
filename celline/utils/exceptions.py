class NullPointException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Null point exception\n{message}")
