

from typing import Dict
from loguru import logger
from pydantic import BaseModel
from fastapi import FastAPI
from mangum import Mangum

from model.classifier import NewsCategoryClassifier

class PredictRequest(BaseModel):
    source: str
    url: str
    title: str
    description: str


class PredictResponse(BaseModel):
    scores: dict
    label: str


app = FastAPI()
data = {}

global_config = {
    "word_vector_model": 'glove-wiki-gigaword-100',
    "word_vector_dim": 100,
    "serialized_model_path": "news_classifier.joblib"
}

@app.on_event("startup")
def startup_event():
    """
    Initialize the `NewsCategoryClassifier` instance to make predictions online. 
    You should pass any relevant config parameters that are needed by NewsCategoryClassifier 
        
    Access to the model instance will be needed in /predict endpoint, make sure you
    store references to them in the data = {} dictionary
    """
    classifier = NewsCategoryClassifier(config={
        'word_vector_model': global_config["word_vector_model"],
        'word_vector_dim': global_config["word_vector_dim"]
    })
    classifier.load(global_config["serialized_model_path"])
    data['model'] = classifier
    logger.info("Setup completed")


@app.on_event("shutdown")
def shutdown_event():
    del data['model']
    logger.info("Shutting down application")


@app.post("/predict")
def predict(request: PredictRequest):
    """Run model inference for incoming request. Return predicted news category and scores

    Args:
        request (PredictRequest): News article for which we want to predict the category

    Returns:
        Dict: {"label": <predicted label>, "scores": label-->score for each category}
    """

    """
    [TO BE IMPLEMENTED]
    1. run model inference and get model predictions for model inputs specified in `request`
    2. Log the following data using logger.info(...)
        {
            'timestamp': <YYYY:MM:DD HH:MM:SS> format, when the request was received,
            'request': dictionary representation of the input request,
            'prediction': dictionary representation of the response,
            'latency': time it took to serve the request, in millisec
        }
    3. Return the predicted label and scores
    """
    logger.info(request)
    return {'label': 'NOT IMPLEMENTED', 'scores': {}}


@app.get("/")
def read_root():
    return {"Hello": "World"}


def handler(event, context):
    asgi_handler = Mangum(app)
    # Call the instance with the event arguments
    response = asgi_handler(event, context)
    return response

