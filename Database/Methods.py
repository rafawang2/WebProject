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

def Generate_BID(gid):
    game_num = {
        1:"G1",
        2:"G2",
        3:"G3",
        4:"G4"
    }
    json_file = "Database/varble.json"
    data = None
    with open(json_file, "r", encoding="utf-8") as file:
        f = file.read()
        data = json.loads(f)
         
    Bid =f"{gid}{data[game_num[gid]]:010d}"

    with open(json_file, "w", encoding="utf-8") as file:
        data[game_num[gid]] += 1
        w = json.dumps(data)
        file.write(w)
        file.close()
        
    return Bid

def Create_Data(table:str,data:dict):
    engine = Connect_DB()
    with engine.connect() as connection:
        command = Insert_to_table(table,data)
        res = connection.execute(text(command))
        connection.commit()
        
        
def Get_BID(condition:dict):
    engine = Connect_DB()
    with engine.connect() as connection:
        command = Select_from_table("UB",['BoardID','Player1','Player2'],condition)
        res = connection.execute(text(command))
        rows = res.fetchall()
        if len(rows) != 0 :
            return rows[0][0]

        else:
            return None
        
def Update_Table(table,data:dict,condition:dict):
    
    cols = list(data.keys())
    vals = list(data.values())
    set_part = Generate_Update_Part(cols,vals)

    cols = list(condition.keys())
    vals = list(condition.values())
    where_part = Generate_Update_Part(cols,vals)

    command = f'UPDATE [{table}] SET {set_part} WHERE {where_part}'
    
    engine = Connect_DB()
    with engine.connect() as connection:
        res = connection.execute(text(command))
        connection.commit()


def Get_Records(RID,items:list):
    command = Select_from_table("Records",items,{"RecordID":RID})
    engine = Connect_DB()
    with engine.connect() as connection:
        res = connection.execute(text(command))
        rows = res.fetchall()
        return rows