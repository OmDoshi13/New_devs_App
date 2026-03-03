from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

# Tenant-to-properties mapping (matches database/seed.sql)
TENANT_PROPERTIES = {
    'tenant-a': [
        {'id': 'prop-001', 'name': 'Beach House Alpha'},
        {'id': 'prop-002', 'name': 'City Apartment Downtown'},
        {'id': 'prop-003', 'name': 'Country Villa Estate'},
    ],
    'tenant-b': [
        {'id': 'prop-001', 'name': 'Mountain Lodge Beta'},
        {'id': 'prop-004', 'name': 'Lakeside Cottage'},
        {'id': 'prop-005', 'name': 'Urban Loft Modern'},
    ]
}


@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """Return properties visible to the current tenant."""
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context not available")
    return TENANT_PROPERTIES.get(tenant_id, [])


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context not available")
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # Round to 2 decimal places using Decimal to avoid float precision errors
    total_decimal = Decimal(revenue_data['total']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": float(total_decimal),
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
