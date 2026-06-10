from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report_schema import ReportCreate, ReportUpdate
from fastapi import HTTPException, status

def create_report(db: Session, report_data: ReportCreate, reporter_id: int):
    # Basic validation of target_type
    valid_types = ['boarding_house', 'review', 'user']
    if report_data.target_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target_type. Must be one of {valid_types}"
        )

    db_report = Report(
        **report_data.model_dump(),
        reporter_id=reporter_id
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

def update_report_status(db: Session, report_id: int, update_data: ReportUpdate):
    report = get_report(db, report_id)
    report.status = update_data.status
    db.commit()
    db.refresh(report)
    return report
