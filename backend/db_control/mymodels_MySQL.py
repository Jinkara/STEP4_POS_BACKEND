from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customers(Base):
    __tablename__ = 'customers'
    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(10))


class Items(Base):
    __tablename__ = 'items'
    item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)


class Purchases(Base):
    __tablename__ = 'purchases'
    purchase_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(10), ForeignKey("customers.customer_id"))
    purchase_date: Mapped[str] = mapped_column(String(10))


class PurchaseDetails(Base):
    __tablename__ = 'purchase_details'
    detail_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    purchase_id: Mapped[str] = mapped_column(String(10), ForeignKey("purchases.purchase_id"))
    item_id: Mapped[str] = mapped_column(String(10), ForeignKey("items.item_id"))
    quantity: Mapped[int] = mapped_column(Integer)

    # ここからPOSのために追加分
# 末尾に追記（既存の import/ Base を流用）
from sqlalchemy import Column, String, Integer, CHAR, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(25), unique=True, nullable=False)       # JANコード
    name = Column(String(100), nullable=False)
    item_code = Column(String(20), nullable=True)
    price_tax_included = Column(Integer, nullable=False)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    emp_cd  = Column(CHAR(10), nullable=False)
    store_cd = Column(CHAR(5), nullable=False)
    pos_no  = Column(CHAR(3), nullable=False)
    total_amt = Column(Integer, nullable=False, default=0)        # 税込
    total_amt_ex_tax = Column(Integer, nullable=False, default=0) # 今回は0でOK
    details = relationship("TradeDetail", back_populates="trade", cascade="all, delete-orphan")

class TradeDetail(Base):
    __tablename__ = "trade_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    prod_code  = Column(String(25), nullable=False)
    prod_name  = Column(String(100), nullable=False)
    prod_price = Column(Integer, nullable=False)
    quantity   = Column(Integer, nullable=False, default=1)
    trade = relationship("Trade", back_populates="details")
