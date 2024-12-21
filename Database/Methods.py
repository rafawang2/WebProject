from Database.Utils import *
from sqlalchemy import text
from datetime import datetime
import json

def Generate_UID():
    
    json_file = "Database/varble.json"
    data = None
    with open(json_file, "r", encoding="utf-8") as file:
        f = file.read()
        data = json.loads(f)
       
    now = datetime.now().strftime("%Y%m%d")
    if now != data["last_date"] :
        data["number"] = 1
                
    Uid =f"{now}{data["number"]:06d}"

    with open(json_file, "w", encoding="utf-8") as file:
        data["number"] += 1
        data["last_date"] = now
        w = json.dumps(data)
        file.write(w)
        file.close()
        
    return Uid
    
def Check_Username(username):
    engine = Connect_DB()
    
    with engine.connect() as connection:
        condition={"Nickname":username}
        command = Select_from_table("User",['UserID','Nickname'],condition)
        res = connection.execute(text(command))
        rows = res.fetchall()
        
        if len(rows) == 1:
            return rows[0][0]
        
        else:
            UID = Generate_UID()
            data = {
                "UserID":UID,
                "Nickname":username
            }
            command = Insert_to_table("User",data)
            res = connection.execute(text(command))
            # Create Records 
            for i in range(1,5):
                data ={
                    'RecordID':f"{i}_{UID}",
                    'UserID':UID,
                    'GameID':i,
                    'Total':0,
                    'Win':0,
                    'Lose':0,
                    'Draw':0,
                    'Unfinish':0
                }
                command = Insert_to_table("Records",data)
                res = connection.execute(text(command))
            connection.commit()
            
        return UID
