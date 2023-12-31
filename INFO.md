### Description:
This solution will allow you to perform predict action using dataloop model management without deploying your model into dataloop and using the docker as a proxy server

The Docker template has an API server that receives an image as input, sends it to a model for prediction, and sends the model 
results in JSON format.

The solution also comes with a test script that parses the API server results and uploads them to the Dataloop platform.

### Install the Application
Follow the instructions under the [repository README file](https://github.com/dataloop-ai-joint-dev/dockerized-server/blob/master/README.md).

### Technology
* Python
* FastAPI
* Docker
