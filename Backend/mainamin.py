from fastapi import FastAPI, UploadFile
import hashlib
import shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
import pika

#start it with: uvicorn  main:app --reload --host 0.0.0.0 --port 8081
app = FastAPI()

# ---- ENABLE CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
file_number = 1

@app.post("/api/analyze")
async def upload(file: UploadFile):
    try:
        file_id = str(uuid.uuid4())
        global file_number
        
        file_path = f"{UPLOAD_DIR}/{file.filename}"
        file_number += 1

        # Save
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
#RabbitMQ: connect to the RabbitMQ server and set a channel and then a slot to send the file path to a queue in that slot
# to start the server: docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672  rabbitmq:4-management
#                                                             srvr port     mgmt port
        #    Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        channel = connection.channel()

        #  Create the queue if it doesn't exist
        channel.queue_declare(queue='vm_tasks')

        #  Send the file path as the message body
        channel.basic_publish(#send to the queue
            exchange='',
            routing_key='vm_tasks',#where to send the body
            body=file_path
        )

        connection.close()

        # Hash
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)

        digest = sha256.hexdigest()
        return {"status": "Task queued","id": file_id, "hash": digest}
    except Exception as e:
        return {"status": str(e),"id":"" , "hash": ""}
