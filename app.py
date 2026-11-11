import os
import json
import boto3
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

TOKEN = os.getenv("HF_TOKEN")
BUCKET_NAME = os.getenv("BUCKET_NAME")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")

s3_client = boto3.client(
    's3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-1'
)

class Memory(BaseModel):
    profile: str = ""
    preferences: list = []
    important_events: list = []
    current_context: str = ""
    boundaries: list = []

def authorize(authorization: str):
    if not authorization or authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/memory")
def read_memory(authorization: str = Header(default=None)):
    authorize(authorization)
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key="memory.json")
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data
    except s3_client.exceptions.NoSuchKey:
        return Memory().model_dump()
    except Exception as e:
        return {"error": str(e)}

@app.post("/memory")
def write_memory(data: Memory, authorization: str = Header(default=None)):
    authorize(authorization)
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key="memory.json",
            Body=json.dumps(data.model_dump(), ensure_ascii=False, indent=2),
            ContentType="application/json"
        )
        return {"saved": True}
    except Exception as e:
        return {"error": str(e)}
