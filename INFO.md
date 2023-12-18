### Description:
A Docker with API server that receives image as an input, send it to a model for prediction, and sends the model 
results in json format.

**Notice:** Make sure to update the requested `host` and `port` in the file: [Dockerfile](app%2FDockerfile), 
before building the docker image: 
1. `EXPOSE 9000` - (line 14)
2. `CMD ["python", "app.py", "--host=0.0.0.0", "--port=9000"]` - (line 17)

### Install the Application
See the sections: `How to Run Locally` and `How to Run Remotely` in the `README.md` repository file.

### Technology
* Python
* FastAPI
* Docker
