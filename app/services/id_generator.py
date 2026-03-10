from __future__ import annotations

from sqlalchemy.orm import Session


def next_code(
    db: Session,
    *,
    model,
    id_attr: str,
    prefix: str,
    width: int = 3,
) -> str:
    """
    Sinh mã dạng PREFIX001, PREFIX002...
    Dựa trên các ID hiện có bắt đầu bằng prefix.
    """
    col = getattr(model, id_attr)
    rows = db.query(col).filter(col.like(f"{prefix}%")).all()

    max_num = 0
    for (val,) in rows:
        if not isinstance(val, str) or not val.startswith(prefix):
            continue
        suffix = val[len(prefix):]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"{prefix}{max_num + 1:0{width}d}"