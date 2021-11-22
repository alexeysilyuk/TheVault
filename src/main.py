from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
from typing import Tuple
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import redis
import os
import logging
from fastapi import Request, FastAPI, status, Form
from fastapi.templating import Jinja2Templates

load_dotenv()  # take environment variables from .env.
logger = logging.getLogger(__name__)

class Encryptor():
    def encrypt(data: str) -> Tuple[str,str]:
        key = Fernet.generate_key()
        fernet = Fernet(key)
        return (key.decode(), fernet.encrypt(data.encode()).decode())
    def decryptData(key:str, data: str) -> str:
        fernet = Fernet(key.encode())
        decMessage = fernet.decrypt(data.encode()).decode()
        return decMessage

class Store(object):
    def store(self, key:str, data:str)->bool:
        pass

    def restore(self, key: str) -> Tuple[bool, str]:
        pass

class FileStore(Store):
    def __init__(self, path:str='storage.txt'):
        self.path = path

    def store(self, key:str, data:str)->bool:
        try:
            with open(self.path, "a") as fileStorage:
                fileStorage.write(key+":"+data+"\n")
            return True
        except Exception:
            logger.error("Failed to write data to file")
            return False

    def restore(self, key: str) -> Tuple[bool, str]:
        result: tuple[bool,str] = (False,"")
        with open(self.path, "r+") as fileStorage:
            lines = fileStorage.readlines()
            fileStorage.seek(0)
            for line in lines:
                currentKey = line.split(':')[0]
                if currentKey != key:
                    fileStorage.write(line)
                else:
                    result = (True,line.split(':')[1])
            fileStorage.truncate()
        return result


class RedisStore(object):
    def __init__(self, hostname:str='localhost', port: str='6379', db_id: int=0):
        self.hostname = hostname
        self.port = port
        self.db = db_id
        self.connection = redis.Redis(host=self.hostname,port=self.port, db=self.db)

    def store(self, key:str, data:str)->bool:
        try:
            self.connection.set(key, data)
            self.connection.expire(key, os.environ.get("REDIS_KEY_TTL_SECONDS"))
            return True
        except Exception:
            logger.error("Connection with Redis failed")
            return False

    def restore(self, key: str) -> Tuple[bool, str]:
        try:
            data = self.connection.get(key)
            self.connection.delete(key)
            return (True,str(data.decode()))
        except Exception:
            logger.error("Connection with Redis failed")
            return (False,"")

class Vault():
    def __init__(self, 
                        redisStore: Store = RedisStore(os.environ.get('REDIS_HOST_NAME'),os.environ.get('REDIS_PORT'),os.environ.get('REDIS_DB_ID')), 
                        fileStore: Store = FileStore(os.environ.get('STORAGE_FILE_NAME'))):

        self.redisClient = redisStore
        self.fileClient = fileStore

    def put(self, storeType: str, data: str) -> Tuple[bool, str]:
        encryptedData: tuple[str,str] = Encryptor.encrypt(data)
        result:bool = False
        if storeType == "volatile":
            result = self.redisClient.store(encryptedData[0],encryptedData[1])
        elif storeType == "persistent":
            result = self.fileClient.store(encryptedData[0],encryptedData[1])
        else:
            pass

        if result == True:
            return (True, encryptedData[0])
        else:
            return (False,"")

    def get(self, key: str) -> Tuple[bool, str]:
        try:
            result: tuple[bool, str] = self.redisClient.restore(key) # Check first in Ram memory
            if result[0] == True:
                parsed : str = Encryptor.decryptData(key,result[1])
                return (True,parsed)
            else:
                result = self.fileClient.restore(key) # No found in redis, try in file
                if result[0] == True:
                    parsed : str = Encryptor.decryptData(key,result[1])
                    return (True,parsed)
                else:
                    return (False,"")
        except Exception:
            return (False,"")


app = FastAPI()

@app.post("/api/encrypt",status_code=status.HTTP_400_BAD_REQUEST)
async def encrypt_api(storeType: str, data: str = Form(...)):

    if storeType not in ["volatile","persistent"]:
        return JSONResponse(content={"msg": "Unsupported storeType provided"})
    vault = Vault()
    
    result: tuple[bool, str] = vault.put(storeType, data)
    if result[0]:
        return JSONResponse(content={"key": result[1]},status_code=status.HTTP_201_CREATED)
    else:
        return JSONResponse(content={"msg":"Storing data failed"},status_code=status.HTTP_400_BAD_REQUEST)

@app.get("/api/decrypt")
async def decrypt_api(keyName: str):
    vault = Vault()
    result :tuple[bool,str] = vault.get(keyName)
    if result[0] == False:
        return JSONResponse(content={"msg":"Key incorrect or data missing"},status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return JSONResponse(content={"data": result[1]},status_code=status.HTTP_200_OK)

templates = Jinja2Templates(directory="html")
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html",{'request':request})


if __name__ == '__main__':
    uvicorn.run(app, port=int(os.environ.get('BACKEND_PORT')), host=os.environ.get('BACKEND_IP'))
