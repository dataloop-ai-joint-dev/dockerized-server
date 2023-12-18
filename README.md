# Dockerized Server

A Docker with API server that receives image as an input, send it to a model for prediction, and sends the model 
results in json format.

**Notice:** Make sure to update the requested `host` and `port` in the file: [Dockerfile](app%2FDockerfile), 
before building the docker image: 
1. `EXPOSE 9000` - (line 14)
2. `CMD ["python", "app.py", "--host=0.0.0.0", "--port=9000"]` - (line 17)


### Solution Components: 

The solution is composed of:
1. [Dockerfile](app%2FDockerfile) - Docker recipe for building the model predict server API.
2. [app.py](app%2Fapp.py) - The server API source code.
3. [dataloop_test.py](dataloop_test.py) - Test script to test the server locally and from the docker.

### Prerequisite:

1. Install the requirements inside the `requirements.txt` file.
2. (Must) Update the function: `model_predict` to call the requested model `predict` function
   and update the returned output as required.
3. (Must) Update the functions: `import_data` and `export_data` to support connection to a real Remote Database
   (Google Cloud Storage, Microsoft Azure, Amazon S3, etc...)
   1. `import_data` - The function connects to the database and overwrite the existing data of the server in 
      `server_predict_results`. \
      `True` is returned on success, otherwise `False`.
   2. `export_data` - The function connects to the database and update the database with the most recent data of the 
   server in `server_predict_results`. \
   `True` is returned on success, otherwise `False`. \
   **Notice:** The function receive the inputs: `request_id` and `to_delete` to handle the following cases:
      1. Backup of a single predict_request (`request_id=<not None>` and `to_delete=False`)
      2. Backup of all the data (`request_id=None` and `to_delete=False`)
      3. Delete of a single predict_request (`request_id=<not None>` and `to_delete=True`)
      4. (Optional) Delete of all the data (`request_id=None` and `to_delete=True`)
   

### How to Run Locally:
In order to test the server locally:
1. Run the following command on the terminal:
```
./app/app.py --host=0.0.0.0 --port=9000
```
2. In the script: [dataloop_test.py](dataloop_test.py), update the `item_id` in the function `main` and run it.

In order to test the server docker image locally:
1. Run the following commands on the terminal:
```
docker build -t fastapi-server .
docker run -p 8000:9000 fastapi-server
```
2. In the script: [dataloop_test.py](dataloop_test.py), update the `item_id` in the function `main` and run it.

### How to Run Remotely:
In order to save the docker in `dockerhub` and use it:
1. Build and save your docker in `dockerhub` using the following commands (inside the Dockerfile directory):
```
docker build -t <docker-repo>/fastapi-server:1.0.0 .
docker login
docker push <docker-repo>/fastapi-server:1.0.0
```
2. Pull the saved docker from `dockerhub` using the command:
```
docker pull <docker-repo>/fastapi-server:1.0.0
```
3. Run the docker image using the command:
```
docker run -p 8000:9000 <docker-repo>/fastapi-server
```

### API Explanation:
The server API support the following API requests:
1. `Get`->`http://0.0.0.0:9000/status` - Validate that the server is up.
2. `Get`->`http://0.0.0.0:9000/predictResults` - Get all the available predict results.
3. `Get`->`http://0.0.0.0:9000/predictResults/{request_id}` - Get the predict result of the given `request_id`.
4. `Post`->`http://0.0.0.0:9000/predict` - Sends the input image to the `model_predict` function and returns the 
`request_id` with its results. (This endpoint in `blocking`) \
The function receives 2 parameters: 
   1. `image` - image file to send for the model predict function
   2. `save_locally` - flag to determine if the image will get saved locally on the server or not.
5. `Post`->`http://0.0.0.0:9000/asyncPredict` - Sends the input image to the `model_predict` function as a 
`background task` and returns the `request_id` for where the results will be updated. (This endpoint in `non-blocking`) \
The function receives 2 parameters: 
   1. `image` - image file to send for the model predict function
   2. `save_locally` - flag to determine if the image will get saved locally on the server or not. \
   (And call `export_data` after predict completed)
6. `Delete`->`http://0.0.0.0:9000/delete/{request_id}` - Delete the predict result of the given `request_id`. \
(And call `export` after delete completed)

And with the following Optional API requests:
1. `Delete`->`http://0.0.0.0:9000/deleteAll` - Delete all the available predict results.
2. `Post`->`http://0.0.0.0:9000/import` - Import the data to the `server_predict_results`. \
(This endpoint is used for load the current data from a remote database and `overwrite` the existing data on the server)
3. `Post`->`http://0.0.0.0:9000/export` - Export the data of the `server_predict_results`. \
(This endpoint is used for backup the current data to a remote database)

### Dataloop Test Explanation:
Test script that test the API `Post` endpoint,
and convert the model results to annotation which gets uploaded to the item in the Dataloop platform.

### Requirements:

`dtlpy` \
`requests` \
`fastapi` \
`uvicorn` \
`python-multipart`
