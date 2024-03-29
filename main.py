from datetime import datetime

from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = FastAPI()
Base = declarative_base()


class MyDB(Base):
    __tablename__ = "db"
    id = Column(Integer, primary_key=True)
    name_device = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)


engine = create_engine("sqlite:///./db.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Statistic(BaseModel):
    x: float
    y: float
    z: float


@app.post("/post/{name_device}")
async def collect_stat(name_device: str, stat: Statistic):
    db_stat = MyDB(name_device=name_device, x=stat.x, y=stat.y, z=stat.z)
    with SessionLocal() as session:
        session.add(db_stat)
        session.commit()
    return "Данные получены"


@app.get("/get/{name_device}")
async def analyze_stat(name_device: str, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None):
    with SessionLocal() as session:
        query = session.query(MyDB).filter(MyDB.name_device == name_device)
        if start_date:
            query = query.filter(MyDB.timestamp >= start_date)
        if end_date:
            query = query.filter(MyDB.timestamp <= end_date)

        statistics = query.all()

    return {
        "statistics": [stat.__dict__ for stat in statistics],
        "X_минимальное": min([stat.x for stat in statistics]),
        "X_максимальное": max([stat.x for stat in statistics]),
        "X_кол-во": len([stat.x for stat in statistics]),
        "X_сумма": sum([stat.x for stat in statistics]),
        "X_медиана": sorted([stat.x for stat in statistics])[len([
            stat.x for stat in statistics]) // 2],

        "Y_минимальное": min([stat.y for stat in statistics]),
        "Y_максимальное": max([stat.y for stat in statistics]),
        "Y_кол-во": len([stat.y for stat in statistics]),
        "Y_сумма": sum([stat.y for stat in statistics]),
        "Y_медиана": sorted([stat.y for stat in statistics])[len(
            [stat.y for stat in statistics]) // 2],

        "Z_минимальное": min([stat.z for stat in statistics]),
        "Z_максимальное": max([stat.z for stat in statistics]),
        "Z_кол-во": len([stat.z for stat in statistics]),
        "Z_сумма": sum([stat.z for stat in statistics]),
        "Z_медиана": sorted([stat.z for stat in statistics])[len(
            [stat.z for stat in statistics]) // 2],
    }
