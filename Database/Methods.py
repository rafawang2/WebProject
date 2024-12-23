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
                
    Uid =f'{now}{data["number"]:06d}'

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

def Get_BID(UID):
    command = f"SELECT * FROM [UB] WHERE Player1 = '{UID}' OR Player2 = '{UID}'"
    engine = Connect_DB()
    with engine.connect() as connection:
        res = connection.execute(text(command))
        rows = res.fetchall()
        return rows

def Get_username(uid1,uid2):
    
    command = f"SELECT [Nickname] FROM [User] WHERE UserID = '{uid1}'"
    data = []
    engine = Connect_DB()
    with engine.connect() as connection:
        res = connection.execute(text(command))
        rows = res.fetchall()
        data.append(rows[0][0])
        
        command = f"SELECT [Nickname] FROM [User] WHERE UserID = '{uid2}'"
        res = connection.execute(text(command))
        rows = res.fetchall()
        data.append(rows[0][0])
    
    return data

def Get_Board(cols,condition):
    command = Select_from_table("Boards",cols,condition)
    
    engine = Connect_DB()
    with engine.connect() as connection:
        res = connection.execute(text(command))
        rows = res.fetchall()
        print(rows)
        return rows[0][0]
    

def Get_Replay(UID):
    Res = {}
    Data = Get_BID(UID)
    for BID,player1,player2 in Data:
        names = Get_username(player1,player2)
        state = Get_Board(['State'],{"BoardID":BID})
        Res[BID] ={
            "GID": int(BID[0]),
            "player1": names[0],
            "player2": names[1],
            "uid1": player1,
            "uid2": player2, 
            "state": state
        }
        
    return Res
