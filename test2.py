from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main1 import WalletQuery, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def test_db_write():

    db = TestingSessionLocal()


    wallet = WalletQuery(address="TXYZ...TEST")
    db.add(wallet)
    db.commit()


    result = db.query(WalletQuery).filter_by(address="TXYZ...TEST").first()
    assert result is not None
    assert result.address == "TXYZ...TEST"
