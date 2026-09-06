import importlib


def test_case_records_are_persisted_in_sqlalchemy_store(tmp_path, monkeypatch):
    db_path = tmp_path / 'govbridge.sqlite3'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_path}')

    import app.core.database as database
    importlib.reload(database)

    database.init_db()

    with database.SessionLocal() as session:
        case = database.CaseRecord(
            case_id='CASE-DB-001',
            service_id='scholarship',
            applicant_name='Database User',
            status='DRAFT',
            decision='{}',
            review='{}',
            timeline='[]',
            department_checks='[]',
        )
        session.add(case)
        session.commit()

    with database.SessionLocal() as session:
        saved = session.query(database.CaseRecord).filter_by(case_id='CASE-DB-001').first()
        assert saved is not None
        assert saved.applicant_name == 'Database User'
        assert saved.service_id == 'scholarship'
