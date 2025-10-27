from pydantic import BaseModel

class ProductOut(BaseModel):
    code: str
    name: str
    price_tax_included: int
