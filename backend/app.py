from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_control.schemas import ProductOut
import requests
import json
# from db_control import crud, mymodels
from db_control import crud, mymodels_MySQL as mymodels

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str


app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/customers")
def create_customer(customer: Customer):
    values = customer.dict()
    tmp = crud.myinsert(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))

    if result:
        result_obj = json.loads(result)
        return result_obj if result_obj else None
    return None


@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    # 結果がNoneの場合は空配列を返す
    if not result:
        return []
    # JSON文字列をPythonオブジェクトに変換
    return json.loads(result)


@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    values_original = values.copy()
    tmp = crud.myupdate(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values_original.get("customer_id"))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    result = crud.mydelete(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}


@app.get("/fetchtest")
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()


# ここからPOSのために追加分
# app.py の先頭付近の import 群に追記
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db_control.connect_MySQL import engine
from db_control.mymodels_MySQL import Product, Trade, TradeDetail

# セッションファクトリ（既存crudと同様のエンジン）
SessionLocal = sessionmaker(bind=engine)

# --- Pydantic Schemas（軽量にこのファイル内で定義） ---
from pydantic import BaseModel
from typing import List

class ProductOut(BaseModel):
    code: str
    name: str
    price_tax_included: int
    class Config:
        from_attributes = True  # pydantic v2

class PurchaseItemIn(BaseModel):
    code: str
    quantity: int

class PurchaseIn(BaseModel):
    empCd: str
    storeCd: str
    posNo: str
    items: List[PurchaseItemIn]

class PurchaseOut(BaseModel):
    success: bool
    tradeId: int
    totalTaxIncluded: int
    totalExTax: int

@app.get("/products/{code}", response_model=ProductOut)
def get_product(code: str):
    session = SessionLocal()
    try:
        stmt = select(Product).where(Product.code == code)
        p = session.execute(stmt).scalars().first()
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductOut(code=p.code, name=p.name, price_tax_included=p.price_tax_included)
    finally:
        session.close()

@app.post("/purchases", response_model=PurchaseOut)
def create_purchase(payload: PurchaseIn):
    session = SessionLocal()
    try:
        # コード一覧で商品一括取得
        codes = [i.code for i in payload.items]
        if not codes:
            raise HTTPException(status_code=400, detail="No items")

        products = (
            session.query(Product)
            .filter(Product.code.in_(codes))
            .all()
        )
        prod_map = {p.code: p for p in products}

        # 明細生成と合計
        total = 0
        details = []
        for it in payload.items:
            p = prod_map.get(it.code)
            if not p:
                # 商品未登録 → スキップ（MVP方針）
                continue
            line = p.price_tax_included * it.quantity
            total += line
            details.append(
                TradeDetail(
                    prod_code=p.code,
                    prod_name=p.name,
                    prod_price=p.price_tax_included,
                    quantity=it.quantity,
                )
            )

        trade = Trade(
            emp_cd=payload.empCd,
            store_cd=payload.storeCd,
            pos_no=payload.posNo,
            total_amt=total,
            total_amt_ex_tax=0,
        )
        trade.details = details

        session.add(trade)
        session.commit()
        session.refresh(trade)

        return PurchaseOut(
            success=True,
            tradeId=trade.id,
            totalTaxIncluded=trade.total_amt,
            totalExTax=trade.total_amt_ex_tax,
        )
    finally:
        session.close()
