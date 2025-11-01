from pathlib import Path


def load_query(base_file: str, name: str) -> str:
    sql_dir = Path(base_file).parent / "queries"
    return (sql_dir / f"{name}.sql").read_text()
