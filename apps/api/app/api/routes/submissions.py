from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import limit_submissions
from app.db.session import get_db
from app.schemas.submissions import SubmissionAssetUploadOut, SubmissionCreate, SubmissionOut
from app.services.artifacts import write_submission_upload
from app.services.submissions.service import create_submission

router = APIRouter(tags=["submissions"])


@router.post("/submission-assets/upload", response_model=SubmissionAssetUploadOut, status_code=status.HTTP_201_CREATED)
async def upload_submission_asset(
    file: UploadFile = File(...),
    _: None = Depends(limit_submissions),
) -> SubmissionAssetUploadOut:
    settings = get_settings()
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    max_bytes = settings.upload_max_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Uploaded file exceeds {settings.upload_max_mb} MB limit")

    try:
        stored = write_submission_upload(
            file_name=file.filename or "proof-upload",
            content_type=file.content_type or "application/octet-stream",
            data=content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SubmissionAssetUploadOut(
        asset_path=stored.asset_path,
        content_type=stored.content_type,
        file_name=stored.file_name,
        byte_size=stored.byte_size,
    )


@router.post("/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
def post_submission(
    payload: SubmissionCreate,
    _: None = Depends(limit_submissions),
    db: Session = Depends(get_db),
) -> SubmissionOut:
    submission = create_submission(db, payload)
    db.commit()
    db.refresh(submission)
    return SubmissionOut.model_validate(submission)
