"""Скрипт для экспорта актуальной OpenAPI спецификации в backend/docs/."""

from pathlib import Path

import yaml

from main import app


def export_openapi() -> None:
    schema = app.openapi()
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    yaml_path = docs_dir / "openapi.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(schema, f, sort_keys=False, allow_unicode=True)

    print(f"OpenAPI spec exported to:\n  - {yaml_path}\n")


if __name__ == "__main__":
    export_openapi()
