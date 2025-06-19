import json

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.helpers import messages
from app.helpers.database import get_db
from app.helpers.exceptions import NotFound, PermissionDeniedError, ValidationError
from app.helpers.middlewares import is_logged_in_middleware
from app.helpers.pinata import upload_file_to_pinata, upload_json_to_pinata
from app.helpers.response import Response, serialize_response

from .crud import (
    create_new_company,
    get_company_by_name,
    save_nft,
    update_token_info,
    user_owns_company,
)
from .schemas import (
    CompanyCreateSchema,
    CompanyProfileResponse,
    MintedNFTCreate,
    MintedNFTOut,
    MintedNFTUpdateToken,
)

router = APIRouter(
    prefix="/company",
    tags=["company"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/create-company")
async def create_company(
    company: CompanyCreateSchema,
    db: Session = Depends(get_db),
    user=Depends(is_logged_in_middleware()),
):

    company_profile = get_company_by_name(db, company.company_name, user.id)
    if company_profile:
        raise ValidationError(messages.COMPANY_EXISTS)

    new_company = create_new_company(db, user.id, company)

    return Response(
        data=serialize_response(CompanyProfileResponse, new_company),
        message=messages.SUCCESS,
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/create-nft")
async def create_nft(
    image: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    attributes: str = Form(None),
    company_id: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(is_logged_in_middleware()),
):
    if not user_owns_company(db, user.id, company_id):
        raise PermissionDeniedError()

    image_bytes = await image.read()
    image_ipfs_uri = upload_file_to_pinata(image_bytes, image.filename)
    attributes_list = json.loads(attributes) if attributes else []

    metadata = {
        "name": name,
        "description": description,
        "image": image_ipfs_uri,
        "attributes": attributes_list,
        "company_id": company_id,
    }
    token_uri = upload_json_to_pinata(metadata)

    nft = MintedNFTCreate(
        company_id=company_id,
        name=name,
        description=description,
        metadata_ipfs_url=token_uri,
        metadata_json=metadata,
        chain="polygon",
    )

    minted_nft = save_nft(db, nft)

    return Response(
        data=dict(token_uri=token_uri, id=minted_nft.id),
        message=messages.SUCCESS,
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/minted-nfts/{nft_id}")
def update_minted_nft_token_info(
    nft_id: int,
    data: MintedNFTUpdateToken,
    db: Session = Depends(get_db),
    user=Depends(is_logged_in_middleware()),
):
    if not user_owns_company(db, user.id, data.company_id):
        raise PermissionDeniedError()

    updated_nft = update_token_info(
        db, nft_id, data.company_id, data.token_id, data.recipient_address
    )
    if not updated_nft:
        raise NotFound()

    return Response(
        data=serialize_response(MintedNFTOut, updated_nft),
        message=messages.SUCCESS,
        status_code=status.HTTP_200_OK,
    )
