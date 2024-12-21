from  Database.Config import *
from sqlalchemy import create_engine
from datetime import datetime

def Generate_UID(last,number):
    now = datetime.now().strftime("%Y%m%d")
    if now != last:
        number = 1;
    return f"{now}{number:06d}"
def Get_String(input,mode:int):
# mode: 決定input 為 list or dict
    keys = []
    values = []
    cols = ""
    vals = ""
    if mode == 0:
        keys = list(input.keys())
        values = list(input.values())
        for i in range(len(keys)):
            data = values[i]
            if type(data) == str:
                val = f"'{data}'"
            else:
                val = data
            
            if i != len(keys)-1:
                cols += f"{keys[i]},"
                vals += f"{val},"
            else :
                cols += f"{keys[i]}"
                vals += f"{val}"
        return cols,vals
    
    elif mode == 1:
        for data in input:
            if data != input[len(input)-1]:
                cols += f"[{data}],"
            else:
                cols += f"[{data}]"
        
        return cols

def Connect_DB(mode:int = 0):
    engine = None
    if mode == 0:
        engine = create_engine(WINDOWS_CONNECTION)
    else:
        engine = create_engine(USER_CONNECTION)
    return engine

def Insert_to_table(table:str,data:dict):
    
    cols,vals = Get_String(data,0)
    commend = f'INSERT INTO "{table}" ({cols}) VALUES ({vals})'
    return commend

def Select_from_table(table:str,cols:list,condition:dict=None):
    
    col = Get_String(cols,1)
    commend = f'SELECT {col} FROM [{table}]'
    
    if condition != None:
        cond,val = Get_String(condition,0)
        where = f'WHERE {cond} = {val}'
        commend += where
        
    return commend