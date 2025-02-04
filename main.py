from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# ✅ Step 1: Set Up Database Connection
DATABASE_URL = "sqlite:///./items.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Step 2: Define the Database Model
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    is_available = Column(Boolean)

# ✅ Step 3: Create the Database
Base.metadata.create_all(bind=engine)

# ✅ Step 4: Create FastAPI Instance
app = FastAPI()

# ✅ Step 5: Dependency for Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Step 6: Define Pydantic Model for Request Validation
class Item(BaseModel):
    name: str
    price: float
    is_available: bool

# ✅ Step 7: Create a POST Endpoint to Add Items
@app.post("/create-item/")
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(name=item.name, price=item.price, is_available=item.is_available)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item '{db_item.name}' with price {db_item.price} has been added!"}

# ✅ Step 8: Create a GET Endpoint to Retrieve All Items
@app.get("/items/")
def get_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return {"items": items}
