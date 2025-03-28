from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List
from tronpy import Tron
from tronpy.exceptions import AddressNotFound
import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class WalletQuery(Base):
    __tablename__ = "wallet_queries"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)



class WalletQueryRequest(BaseModel):
    address: str


class WalletQueryResponse(BaseModel):
    address: str
    balance: float
    bandwidth: int
    energy: int


class WalletQueryRecord(BaseModel):
    id: int
    address: str
    timestamp: datetime

    class Config:
        orm_mode = True



app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/wallet", response_model=WalletQueryResponse)
def get_wallet_info(request: WalletQueryRequest, db: Session = Depends(get_db)):
    client = Tron()
    try:
        addr = client.get_account(request.address)
        bandwidth = client.get_account_resource(request.address)['free_net_remaining']
        energy = client.get_account_resource(request.address)['energy_remaining']
        balance = addr.get('balance', 0) / 1_000_000
    except AddressNotFound:
        raise HTTPException(status_code=404, detail="Address not found")


    record = WalletQuery(address=request.address)
    db.add(record)
    db.commit()
    db.refresh(record)

    return WalletQueryResponse(address=request.address, balance=balance, bandwidth=bandwidth, energy=energy)


@app.get("/wallets", response_model=List[WalletQueryRecord])
def get_wallet_queries(skip: int = 0, limit: int = Query(default=10, le=100), db: Session = Depends(get_db)):
    return db.query(WalletQuery).order_by(WalletQuery.timestamp.desc()).offset(skip).limit(limit).all()
