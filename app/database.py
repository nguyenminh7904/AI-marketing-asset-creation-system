from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    from app.repositories.models import Asset, AssetEvent
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_assets_table()


def _migrate_sqlite_assets_table():
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    column_defs = {
        "campaign_name": "VARCHAR",
        "brand_name": "VARCHAR",
        "product_condition": "TEXT",
        "key_product_facts": "TEXT",
        "target_audience": "TEXT",
        "customer_persona": "TEXT",
        "platform": "VARCHAR",
        "marketing_objective": "VARCHAR",
        "funnel_stage": "VARCHAR",
        "copy_framework": "VARCHAR",
        "selling_points": "TEXT",
        "price": "VARCHAR",
        "offer": "VARCHAR",
        "language": "VARCHAR",
        "compliance_notes": "TEXT",
        "scene_direction": "TEXT",
        "identity_preservation": "TEXT",
        "claim_safety": "TEXT",
        "campaign_brief_json": "TEXT",
        "prompt_controls_json": "TEXT",
        "review_checklist_json": "TEXT",
        "channel_outputs_json": "TEXT",
        "quality_report_json": "TEXT",
        "selected_variant_id": "VARCHAR",
        "exported_at": "DATETIME",
    }

    with engine.begin() as conn:
        existing = {
            row[1]
            for row in conn.exec_driver_sql("PRAGMA table_info(assets)").fetchall()
        }
        for column_name, column_type in column_defs.items():
            if column_name not in existing:
                conn.exec_driver_sql(
                    f"ALTER TABLE assets ADD COLUMN {column_name} {column_type}"
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
