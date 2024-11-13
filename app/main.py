from fastapi import FastAPI, Response, status
from service.service import verify_and_save_sequence, get_stats
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the mutant detection app."}

@app.get("/stats")
async def get_dna_stats():
    return get_stats()

@app.post("/mutant")
async def filter_mutant(dna_data: dict, response: Response):
    is_mutant = verify_and_save_sequence(dna_data)
    if is_mutant:
        response.status_code = status.HTTP_200_OK
        return {
            "statusCode": 200,
            "message": "Mutant found for recruiting!"
        }
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            "statusCode": 403,
            "message": "Mere human found."
        }