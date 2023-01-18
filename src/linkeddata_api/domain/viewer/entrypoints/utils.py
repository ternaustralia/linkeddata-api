from typing import Optional, Union


def get_optional_value(row: dict, key: str) -> Optional[str]:
    return row.get(key)["value"] if row.get(key) else None


def ceiling_division(a: Union[int, float], b: Union[int, float]) -> int:
    return int(-(a // -b))
