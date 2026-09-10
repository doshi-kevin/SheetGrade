"""Golden snapshot: the full reader output for sample_key.xlsx, frozen to JSON.

A diff here means the reader's output changed. That's sometimes intentional
(you improved something) and sometimes a regression -- either way it should
be a deliberate decision, not a silent side effect, which is the point of a
golden test over a handful of individual assertions.

Regenerate deliberately with:
    uv run python -c "
    import json
    from pathlib import Path
    from sheetgrade.reader import read_xlsx
    from sheetgrade.ir.serialize import workbook_to_dict
    data = workbook_to_dict(read_xlsx(Path('tests/fixtures/keys/sample_key.xlsx')))
    Path('tests/golden/sample_key.json').write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    "
"""

import json
from pathlib import Path

from sheetgrade.ir.serialize import workbook_to_dict
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"
GOLDEN = Path(__file__).parent / "sample_key.json"


def test_reader_output_matches_golden_snapshot() -> None:
    actual = workbook_to_dict(read_xlsx(FIXTURE))
    expected = json.loads(GOLDEN.read_text())
    assert actual == expected
