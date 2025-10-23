import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from app.models import engine, Scan
from app.schemas import ScanRequest, ScanResult, ScanHistoryItem, ScanDetail
from app.services.scanner import AccessibilityScanner

router = APIRouter(prefix="/api", tags=["scan"])
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _clean_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


@router.post("/scan", response_model=ScanDetail)
def scan_url(payload: ScanRequest, db: Session = Depends(get_db)):
    url = _clean_url(payload.url)
    scanner = AccessibilityScanner(url)
    result = scanner.scan()

    scan = Scan(
        url=result["url"],
        title=result["title"],
        score=result["score"],
        total_checks=result["total_checks"],
        passes=result["passes"],
        violations=result["violations"],
        by_impact=json.dumps(result["by_impact"]),
        by_principle=json.dumps(result["by_principle"]),
        issues=json.dumps(result["issues"]),
        summary=result["summary"],
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return ScanDetail(
        id=scan.id,
        url=scan.url,
        title=scan.title,
        score=scan.score,
        total_checks=scan.total_checks,
        passes=scan.passes,
        violations=scan.violations,
        by_impact=json.loads(scan.by_impact),
        by_principle=json.loads(scan.by_principle),
        issues=json.loads(scan.issues),
        summary=scan.summary,
        created_at=scan.created_at,
    )


@router.get("/history", response_model=list[ScanHistoryItem])
def scan_history(db: Session = Depends(get_db)):
    return db.query(Scan).order_by(Scan.created_at.desc()).limit(50).all()


@router.get("/scan/{scan_id}", response_model=ScanDetail)
def scan_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanDetail(
        id=scan.id,
        url=scan.url,
        title=scan.title,
        score=scan.score,
        total_checks=scan.total_checks,
        passes=scan.passes,
        violations=scan.violations,
        by_impact=json.loads(scan.by_impact),
        by_principle=json.loads(scan.by_principle),
        issues=json.loads(scan.issues),
        summary=scan.summary,
        created_at=scan.created_at,
    )
