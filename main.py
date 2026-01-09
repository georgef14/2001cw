from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
import pyodbc
import requests

app=FastAPI()

security=HTTPBasic()

conn=pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=dist-6-505.uopnet.plymouth.ac.uk;DATABASE=YOURDB;UID=YOURUSER;PWD=YOURPASS"
)

def authenticate(credentials:HTTPBasicCredentials=Depends(security)):
    r=requests.get("https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users",auth=(credentials.username,credentials.password))
    if r.status_code!=200:
        raise HTTPException(status_code=401)
    return credentials.username

@app.get("/users")
def get_users(user=Depends(authenticate)):
    cursor=conn.cursor()
    cursor.execute("EXEC CW1.GetUsers")
    rows=cursor.fetchall()
    return [{"UserID":r[0],"Username":r[1],"Email":r[2],"Role":r[3]} for r in rows]

@app.post("/users")
def create_user(username:str,email:str,role:str,user=Depends(authenticate)):
    cursor=conn.cursor()
    cursor.execute("EXEC CW1.CreateUser ?,?,?",username,email,role)
    conn.commit()
    return {"status":"created"}

@app.put("/users/{user_id}")
def update_user(user_id:int,email:str,role:str,user=Depends(authenticate)):
    cursor=conn.cursor()
    cursor.execute("EXEC CW1.UpdateUser ?,?,?",user_id,email,role)
    conn.commit()
    return {"status":"updated"}

@app.delete("/users/{user_id}")
def delete_user(user_id:int,user=Depends(authenticate)):
    cursor=conn.cursor()
    cursor.execute("EXEC CW1.DeleteUser ?",user_id)
    conn.commit()
    return {"status":"deleted"}

@app.get("/profile-view")
def profile_view(user=Depends(authenticate)):
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM CW1.UserProfileView")
    rows=cursor.fetchall()
    return [{"UserID":r[0],"Username":r[1],"Email":r[2],"Role":r[3],"Activity":r[4]} for r in rows]
