from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/ping", status_code=200)
def ping():
    return {"msg": "ok"}
