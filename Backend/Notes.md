Here are some notes of new things we learnt in this project:

+*Fastapi needs the UploadFile lib to deal with file uploads*

+*LiveServer bliiid, ken l'script mte3k ya3ml modification (yzid wele yna99as fichieet) fl directories mte3k, yreloadi <=solution=> 
  Settings → search for:*
    `liveServer.settings.ignoreFiles`   *add:* ```"**/uploads/**"```

+*CORS = Cross-Origin Resource Sharing*
It is a browser security rule that controls whether a web page is allowed to make requests to a different origin.

An origin is defined by:
scheme://hostname:port

http://localhost:5500 X http://localhost:8081 are different origins, because the port differs	

A browser will block requests from one origin to another unless the server explicitly says: “Yes, I allow this.”

That “yes” is the CORS headers:
---- ENABLE CORS ----
```
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
FastAPI responded properly to the browser:
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *```


