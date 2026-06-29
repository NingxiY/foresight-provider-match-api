from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/provider-matches", tags=["Provider Matches"])


def _score(provider: models.Provider, state: str, insurance: str | None, concern: str, preferred_day: str | None) -> int:
    score = 0
    if provider.state == state:
        score += 3
    if insurance and provider.accepted_insurance:
        if insurance.lower() in provider.accepted_insurance.lower():
            score += 3
    if provider.specialty and concern.lower() in provider.specialty.lower():
        score += 2
    if provider.accepting_new_patients:
        score += 2
    if preferred_day and provider.available_days:
        if preferred_day.lower() in provider.available_days.lower():
            score += 1
    return score


@router.post("/", response_model=schemas.ProviderMatchOut, status_code=201)
def request_match(
    payload: schemas.ProviderMatchCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    match_request = models.ProviderMatchRequest(
        patient_id=current_user.id,
        state=payload.state,
        insurance=payload.insurance,
        concern=payload.concern,
        preferred_day=payload.preferred_day,
    )
    db.add(match_request)
    db.commit()
    db.refresh(match_request)

    all_providers = db.query(models.Provider).all()
    scored = [
        (p, _score(p, payload.state, payload.insurance, payload.concern, payload.preferred_day))
        for p in all_providers
    ]
    matched = sorted(
        [(p, s) for p, s in scored if s > 0],
        key=lambda x: x[1],
        reverse=True,
    )

    return schemas.ProviderMatchOut(
        id=match_request.id,
        patient_id=match_request.patient_id,
        state=match_request.state,
        insurance=match_request.insurance,
        concern=match_request.concern,
        preferred_day=match_request.preferred_day,
        matched_providers=[
            schemas.ProviderScore(provider=schemas.ProviderOut.model_validate(p), score=s)
            for p, s in matched
        ],
    )
