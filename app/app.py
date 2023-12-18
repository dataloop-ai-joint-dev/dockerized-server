from fastapi import FastAPI, UploadFile, BackgroundTasks
import uvicorn
import time
import argparse
import shutil
import uuid
import datetime
import os
import json

app = FastAPI()
server_url = "http://0.0.0.0:9000"
server_predict_results = dict()


# TODO: Write your model prediction call
def model_predict(image):
    try:
        # Check if image is of type 'UploadFile'
        image_path = image.filename
    except:
        # Check if image is of type 'str' (image filepath)
        if isinstance(image, str):
            image_path = image
        else:
            predict_result = {
                "status": "Fail",
                "response": "Unsupported image format",
                "createdAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            return predict_result

    print("Processing...")
    time.sleep(5)
    print("Done!")

    predict_result = {
        "status": "Success",
        "response": {
            "image": image_path,
            "label": "Dog"
        },
        "createdAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return predict_result


# API predict call handle
def predict(image: UploadFile, save_locally: bool, request_id: str):
    print(f"Received input: (image: {image.filename}, save_locally: {save_locally})")

    try:
        if image.filename != '':
            if save_locally:
                image = save_file_locally(request_id=request_id, image=image)

            predict_result = model_predict(image=image)
            predict_result["request_id"] = request_id
            delete_file_locally(request_id=request_id)
        else:
            predict_result = {
                "request_id": request_id,
                "status": "Fail",
                "response": "No file selected",
                "createdAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }

        server_predict_results[request_id] = predict_result
        export_data(request_id=request_id, to_delete=False)
        return predict_result

    except Exception as e:
        return str(e)


# If you want to save the image locally, use this function
def save_file_locally(request_id: str, image: UploadFile):
    os.makedirs(name=request_id, exist_ok=True)
    filepath = os.path.join(request_id, image.filename)
    with open(filepath, "wb") as local_file:
        shutil.copyfileobj(image.file, local_file)
    return filepath


# If you want to delete the locally saved image, use this function
def delete_file_locally(request_id: str):
    try:
        shutil.rmtree(path=request_id)
        return {"status": "Success"}
    except:
        return {"status": "Success (The file was already deleted)"}


# TODO: Change the implementation of import_data to support import from the remote database
def import_data():
    global server_predict_results

    load_filepath = os.path.join(os.getcwd(), "database.json")
    try:
        with open(load_filepath, 'r') as json_data:
            server_predict_results_list = json.load(fp=json_data)
            for predict_result in server_predict_results_list:
                request_id = predict_result["request_id"]
                server_predict_results[request_id] = predict_result
        return True
    except:
        return False


# TODO: Change the implementation of export_data to support export to the remote database
def export_data(request_id: str = None, to_delete: bool = False):
    global server_predict_results

    # TODO: Implement backup of the given request_id to the database
    if request_id and not to_delete:
        request_result = server_predict_results.get(request_id, None)
        if request_result:
            print(f"Received Request Id: '{request_id}' result")
        else:
            print(f"Failed to get Request Id: '{request_id}' result")
            return False

    # TODO: Implement backup of all the data to the database
    if not request_id and not to_delete:
        print(f"Backup all results")

    # TODO: Implement deletion of the given request_id from the database
    if request_id and to_delete:
        request_result = server_predict_results.pop(request_id, None)
        if request_result:
            print(f"Request Id: '{request_id}' was deleted")
        else:
            print(f"Failed to delete Request Id: '{request_id}' result")
            return False

    # TODO: Implement deletion of all the data on the database (Optional)
    if not request_id and to_delete:
        print(f"Delete all results")
        server_predict_results = dict()

    # Example of Exporting all the data to a local json file
    save_filepath = os.path.join(os.getcwd(), "database.json")
    with open(save_filepath, 'w') as json_data:
        json.dump(obj=list(server_predict_results.values()), fp=json_data, indent=4)
    return True


#################
# API Interface #
#################
@app.get(path='/status')
def status():
    server_status = {"status": "Alive"}
    return server_status


@app.get(path='/predictResults')
def predict_results():
    global server_predict_results
    results = list(server_predict_results.values())
    return results


@app.get(path='/predictResults/{request_id}')
def predict_results(request_id: str):
    global server_predict_results

    try:
        result = dict(server_predict_results[request_id])
    except:
        result = f"Request Id: {request_id}, result wasn't found."

    return result


@app.post(path='/predict')
def sync_predict(image: UploadFile, save_locally: bool = False):
    # Set Pending status
    request_id = str(uuid.uuid4())
    predict_result = {
        "request_id": request_id,
        "status": "Pending",
        "response": "",
        "createdAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    server_predict_results[request_id] = predict_result

    # Sync Request
    predict_result = predict(image=image, save_locally=save_locally, request_id=request_id)
    return predict_result


@app.post(path='/asyncPredict')
def async_predict(background_tasks: BackgroundTasks, image: UploadFile, save_locally: bool = False):
    # Set Pending status
    request_id = str(uuid.uuid4())
    predict_result = {
        "request_id": request_id,
        "status": "Pending",
        "response": "",
        "createdAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    server_predict_results[request_id] = predict_result

    # Async Request (Add to Background Tasks)
    background_tasks.add_task(predict, image, save_locally, request_id)
    async_result = {
        "request_id": request_id,
        "status": "Success",
        "response": "Async request got sent"
    }
    return async_result


# Optional (Can be removed)
@app.delete(path='/deleteAll')
def delete_all():
    delete_status = export_data(request_id=None, to_delete=True)

    if delete_status:
        delete_all_result = {
            "status": "Success",
            "response": "All available data got deleted"
        }
    else:
        delete_all_result = {
            "status": "Failed",
            "response": "Data failed to be deleted. Using the current available data"
        }

    return delete_all_result


@app.delete(path='/delete/{request_id}')
def delete(request_id: str):
    delete_status = export_data(request_id=request_id, to_delete=True)

    if delete_status:
        delete_result = {
            "status": "Success",
            "response": f"Request Id: '{request_id}' got deleted"
        }
    else:
        delete_result = {
            "status": "Fail",
            "response": f"Request Id: '{request_id}' wasn't found",
        }

    return delete_result


#################
# For Debugging #
#################
@app.post(path='/import')
def import_api():
    import_status = import_data()

    if import_status:
        import_result = {
            "status": "Success",
            "response": "Data got imported"
        }
    else:
        import_result = {
            "status": "Fail",
            "response": "Data failed to be imported. Using the current available data"
        }

    return import_result


@app.post(path='/export')
def export_api():
    export_status = export_data(request_id=None, to_delete=False)

    if export_status:
        export_result = {
            "status": "Success",
            "response": "Data got exported"
        }
    else:
        export_result = {
            "status": "Fail",
            "response": "Data failed to get exported"
        }

    return export_result


# @app.post(path='/export/{request_id}')
# def export_api(request_id: str):
#     export_status = export_data(request_id=request_id, to_delete=False)
#
#     if export_status:
#         export_result = {
#             "status": "Success",
#             "response": f"Request Id: '{request_id}' got exported"
#         }
#     else:
#         export_result = {
#             "status": "Fail",
#             "response": f"Request Id: '{request_id}' failed to get exported"
#         }
#
#     return export_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a FastAPI Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help="Host for the FastAPI server (default: '0.0.0.0')")
    parser.add_argument('--port', type=int, default=9000, help="Port for the FastAPI server (default: 9000)")
    args = parser.parse_args()

    host = args.host
    port = args.port
    server_url = f"http://{host}:{port}"

    import_data()
    uvicorn.run(app=app, host=host, port=port)

# Test Server Locally: #
# ./app/app.py --host=0.0.0.0 --port=9000

# Test Server Docker Locally: #
# docker build -t fastapi-server .
# docker run -p 8000:9000 fastapi-server
