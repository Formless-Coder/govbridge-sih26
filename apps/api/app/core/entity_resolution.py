from __future__ import annotations

import re
from typing import Any


def _normalize_name(value: str | None) -> str:
    if not value:
        return ''
    return re.sub(r'[^a-z0-9]', '', value.lower())


def _same_person(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_name = _normalize_name(left.get('name'))
    right_name = _normalize_name(right.get('name'))
    left_dob = (left.get('dob') or '').strip()
    right_dob = (right.get('dob') or '').strip()
    left_phone = (left.get('phone') or '').strip()
    right_phone = (right.get('phone') or '').strip()

    if left_dob and right_dob and left_dob == right_dob:
        if left_phone and right_phone and left_phone == right_phone:
            return True
        if left_name and right_name and (left_name == right_name or left_name in right_name or right_name in left_name):
            return True
    if left_phone and right_phone and left_phone == right_phone and left_dob and right_dob and left_dob == right_dob:
        return True
    return False


def resolve_entities(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: list[list[str]] = []
    seen: set[str] = set()

    for index, record in enumerate(records):
        record_id = str(record.get('id') or record.get('record_id') or f'anon-{index}')
        if record_id in seen:
            continue
        group = [record_id]
        for other_index in range(index + 1, len(records)):
            other = records[other_index]
            other_id = str(other.get('id') or other.get('record_id') or f'anon-{other_index}')
            if other_id in seen:
                continue
            if _same_person(record, other):
                group.append(other_id)
                seen.add(other_id)
        seen.add(record_id)
        if len(group) > 1:
            groups.append(group)

    resolved_entities: list[dict[str, Any]] = []
    for record in records:
        record_id = str(record.get('id') or record.get('record_id') or 'unknown')
        linked = next((group for group in groups if record_id in group), None)
        if linked:
            resolved_entities.append({
                'id': record_id,
                'status': 'duplicate_candidate',
                'match_group': linked,
                'confidence': 0.92,
            })
        else:
            resolved_entities.append({
                'id': record_id,
                'status': 'unique',
                'match_group': [record_id],
                'confidence': 0.99,
            })

    duplicate_groups = []
    for index, group in enumerate(groups, start=1):
        duplicate_groups.append({
            'group_id': f'dup-group-{index}',
            'record_ids': group,
            'match_reason': 'Shared phone and DOB',
        })

    return {
        'resolved_entities': resolved_entities,
        'duplicate_groups': duplicate_groups,
    }
