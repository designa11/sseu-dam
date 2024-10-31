from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import DB_connect
import schema.select_schema as select_schema
import ORM.ORM as ORM
import ipconfig as ip
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
DB_connect.engine
ORM.Base
ORU = ORM.User

# CORS 주소 = 클라이언트 주소
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ip.client_ip],  # 요청을 허용할 출처(origin)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT 등)
    allow_headers=["*"],  # 모든 헤더 허용
)


def get_db(): #Session 초기화 의존성 // 요청처리가 끝난 후 자동으로 정리하기 위해
    db = Session(bind = DB_connect.engine)
    try:
        yield db
    finally:
        db.close()


@app.post("/login") # 로그인 정보를 받아서 반환
def select_login(request: select_schema.LoginSchema, db : Session = Depends(get_db)): #일단 비밀번호해쉬 = 비밀번호 라고 가정########
    db_user = db.query(ORU).filter(ORU.UserID==request.UserID).first() # 검색
    if db_user is None:
        raise HTTPException(status_code=400, detail="아이디 틀림")
    if (db_user.PasswordHash != request.PasswordHash):
        raise HTTPException(status_code=400, detail="비밀번호 틀림")
    return {"message":"로그인 성공"}


@app.post("/signup")
def add_member(member : select_schema.Signup_Schema, db:Session=Depends(get_db)):
    existing_user = db.query(ORM.User).filter(ORM.User.UserID == member.UserID).first()
    # 이미 있는 아이디 인지 확인
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID입니다.")
    ### 등록된 폰인지 확인
    existing_phone = db.query(ORM.User).filter(ORM.User.Phone == member.Phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="이미 사용중인 전화번호입니다.")
    
    db_user = ORM.User(**member.dict(exclude_unset=True))

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return{"message" : "회원가입이 완료되었습니다."}
    
@app.post("/forgot-password") #정보 입력창
def forgot_password(model : select_schema.forgot_Password , db:Session=Depends(get_db)):
    existing_user = db.query(ORM.User).filter(ORM.User.UserID==model.UserID).first()
    if existing_user:
        if existing_user.email==model.email:
            if existing_user.Phone == model.Phone:
                return{"message":f"/{model.UserID}/reset-password"}
            raise HTTPException(status_code=400, detail="폰 번호 다름")
        raise HTTPException(status_code=400, detail="이메일 다름")
    raise HTTPException(status_code=400, detail="아이디가 틀렸습니다.")

@app.post("/{UserID}/reset-password")# 비번 리셋하기
def reset_password(model : select_schema.check_Password, db:Session=Depends(get_db)):
    if model.password == model.password2:
        user = db.query(ORM.User).filter(ORM.User.UserID==model.UserID).first()
        user.PasswordHash = model.password
        db.commit()
        return{"message": "변경 성공"}
    else:
        raise HTTPException(status_code=400, detail="비밀번호 확인 실패")
    
@app.post("/main/alert")## 임시 테스트용  d알람 수신 # json 수정필요
def upload_fall(AlertData: select_schema.pr_schema_SensingAlert, db:Session=Depends(get_db)):

    Alert_Idx_increament = db.query(func.max(ORM.pr_tb_SensingAlerts.AlertIdx)).scalar()
    new_Alert_Idx = (Alert_Idx_increament + 1)

    new_fall_allert = ORM.pr_tb_SensingAlerts(SensingType = AlertData.SensingType, DeviceIdx = AlertData.DeviceIdx, AlertIdx = new_Alert_Idx)
    db.add(new_fall_allert)
    db.commit()
    db.refresh(new_fall_allert)
    return {"message":"수신 완료"}

