# 資料庫table columns
TABLE_COLS ={
        "User":['UserID','Nickname'],
        "Boards":['BoardID','GameID','Steps','State'],
        "UB":['BoardID','Player1','Player2'],
        "Records":['RecordID','UserID','GameID','Total','Win','Lose','Draw','Unfinish'] 
}

# 連接Database的參數
# SERVER = r"" r表示使用原始string，不然會warning 
SERVER = r""
DATABASE = "database_name"
USERNAME = ""
PASSWORD = ""
DRIVER = "ODBC Driver 17 for SQL Server"

# Windows 驗證方式連接資料庫
WINDOWS_CONNECTION = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver={DRIVER}&trusted_connection=yes"
)

# user 認證
USER_CONNECTION = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}"
)