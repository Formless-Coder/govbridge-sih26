import re
from datetime import UTC, datetime


CASE_ID_PATTERN = re.compile(r'^GOV-\d{4}-\d{6}$')


def generate_case_id() -> str:
    year = datetime.now(UTC).strftime('%Y')
    sequence = '000001'
    return f'GOV-{year}-{sequence}'


def is_valid_case_id(case_id: str) -> bool:
    return bool(CASE_ID_PATTERN.match(case_id))
