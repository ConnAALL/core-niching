import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
load_dotenv()
QUEUE_ADDR = os.getenv("QUEUE_ADDR")    

class ChromeID(BaseModel):
    quadrant: int = -1
    file_name: str = ""


class ChromMap(BaseModel):
    chrom_file: str
    agent_name: str


chrom_map = {}
queue_1 = []
queue_2 = []
queue_3 = []
queue_4 = []

stats = {"connections": 0, "error_requests": 0}


queues = [queue_1, queue_2, queue_3, queue_4]

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/update_map")
async def update_map(data: ChromMap):
    #print(data)
    chrom_map.update({data.agent_name: data.chrom_file})
    #print(chrom_map)


@app.get("/get_map_{name}")
def get_map(name):
    return {chrom_map[name]}

    
@app.get("/stats")
def get_stats():
    return stats


@app.get("/is_alive")
def is_alive():
    print("New connection")
    stats["connections"] += 1
    return {0}


@app.get("/check_queues")
def get_queues():
    return {"queues": queues}


@app.get("/req_{num}")
def get_chrom(num):
    num = int(num) - 1
    print("|Q| :  {}, {}, {}, {}".format(len(queue_1), len(queue_2), len(queue_3), len(queue_4)))

    if num < 0 or num > 4:
        stats["error_requests"] += 1
        print("Failed to fetch chromosome from Q:{}".format(num + 1))
        return {"chromosome": -1}

    if len(queues[num]) == 0:
        print("Failed to fetch new chromosome from Q:{}".format(num + 1))
        stats["error_requests"] += 1
        return {"chromosome": -1}

    chromosome = queues[num].pop(0)
    print("Chromosome fetched from Q:{}".format(num + 1))
    return {"chromosome": chromosome}


@app.post("/post")
async def post_data(chromosome: ChromeID):
    if chromosome.quadrant < 1 or chromosome.quadrant > 4:
        stats["error_requests"] += 1

    if chromosome.quadrant == 1:
        if queue_1.count(chromosome.file_name) < 3:
            queue_1.append(chromosome.file_name)
    elif chromosome.quadrant == 2:
        if queue_2.count(chromosome.file_name) < 3:
            queue_2.append(chromosome.file_name)
    elif chromosome.quadrant == 3:
        if queue_3.count(chromosome.file_name) < 3:
            queue_3.append(chromosome.file_name)
    elif chromosome.quadrant == 4:
        if queue_4.count(chromosome.file_name) < 3:
            queue_4.append(chromosome.file_name)

    print("Chromosome added to Q:{}".format(chromosome.quadrant))

    return({"queue_1": queue_1, "queue_2": queue_2, "queue_3": queue_3, 
            "queue_4": queue_4})


@app.get("/info")
def get_info():
    infos = {"chrom_map": chrom_map, "stats": stats, "queues": queues}
    return infos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, QUEUE_ADDR, port=8000)
    #uvicorn.run(app, QUEUE_ADDR, port=8000, log_level="critical")
