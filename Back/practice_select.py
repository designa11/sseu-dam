import DB_connect
import ORM.ORM as ORM
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import schema.select_schema as select_schema


ORM.Base

# ORM.User

def get_db(): #Session 초기화 의존성 // 요청처리가 끝난 후 자동으로 정리하기 위해
    db = Session(bind = DB_connect.engine)
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message" : "basic"}

@app.get("/select/{UserID}", response_model=select_schema.UserSchema)
def read_user(UserID : str, db : Session = Depends(get_db)):
    db_user = db.query(ORM.User).filter(ORM.User.UserID==UserID).first() # 검색
    if db_user is None:
        return {"error" : "존재하지 않는 회원"}
    # return select_schema.UserSchema.model_validate(db_user)
    return db_user

