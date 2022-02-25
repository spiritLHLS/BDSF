from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import models, schemas
import time
import datetime


def get_info_by_id(db: Session, id: int):
    return db.query(models.user).filter(models.user.id == id).first()


def get_info_by_dyid(db: Session, dyid: str):
    return db.query(models.user).filter(models.user.dyid == dyid).first()


def get_all_info(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.user).offset(skip).limit(limit).all()

def get_overdue_info(db: Session):
    # 先获得时间数组格式的日期
    # threeDay = (datetime.datetime.now() + datetime.timedelta(days=3))
    # oneDay = (datetime.datetime.now() - datetime.timedelta(days=1))
    # 转换为时间戳
    timeStampStart = int(time.mktime(datetime.datetime.now().timetuple()))
    # timeStampEnd = int(time.mktime(threeDay.timetuple()))
    return db.query(models.user).filter(models.user.draw_time <= timeStampStart).all()

def get_effective_info(db: Session):
    # 转换为时间戳
    timeStampStart = int(time.mktime(datetime.datetime.now().timetuple()))
    return db.query(models.user).filter(or_(models.user.draw_time >= timeStampStart, models.user.draw_time == 0)).all()

def get_all_info_OfficialLottery(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.user).filter(models.user.hasOfficialLottery == True).offset(skip).limit(limit).all()

def get_all_info_isnotOfficialLottery(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.user).filter(models.user.hasOfficialLottery != True).offset(skip).limit(limit).all()


def create_info(db: Session, user: schemas.Createinfo):
    db_user = models.user(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_info_by_code(db: Session, user):
    db_user = models.user(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_all_info(db: Session, skip: int = 0, limit: int = 10000):
    mod_user = db.query(models.user).offset(skip).limit(limit).all()
    db.delete(mod_user)
    db.commit()
    return mod_user


def delete_info_by_code(db: Session, dyid: str):
    mod_user = db.query(models.user).filter(models.user.dyid == dyid).first()
    db.delete(mod_user)
    db.commit()
    return mod_user

def delete_id_by_code(db: Session, id: int):
    mod_user = db.query(models.user).filter(models.user.id == id).first()
    db.delete(mod_user)
    db.commit()
    return mod_user
