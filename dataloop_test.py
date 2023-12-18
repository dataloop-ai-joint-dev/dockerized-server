import dtlpy as dl
import requests
import time

server_url = "http://0.0.0.0:9000"


def send_image(item: dl.Item, save_locally: bool = False, sync_flag: bool = True):
    try:
        if sync_flag:
            url = f"{server_url}/predict"
        else:
            url = f"{server_url}/asyncPredict"

        files = {'image': item.download(save_locally=False)}

        response = requests.post(url=url, files=files, params={"save_locally": save_locally})
        if response.status_code == 200:
            # Successful response from the server
            json_response = response.json()
            print(json_response)
            return json_response
        else:
            # Handle errors
            print('Error:', response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle exceptions
        print('Request error:', str(e))


def predict_status(request_id: str = None):
    try:
        if request_id:
            url = f"{server_url}/predictResults/{request_id}"
        else:
            url = f"{server_url}/predictResults"

        response = requests.get(url=url)
        if response.status_code == 200:
            # Successful response from the server
            json_response = response.json()
            print(json_response)
            return json_response
        else:
            # Handle errors
            print('Error:', response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle exceptions
        print('Request error:', str(e))


def sync_test():
    # TODO: Update item_id and save_locally
    item_id = '64ef71d84cea7f1a3aaef5ad'
    item = dl.items.get(item_id=item_id)
    save_locally = True

    # API requests to the FastAPI Server
    json_response = send_image(item=item, save_locally=save_locally)

    # Upload Annotation
    if json_response["status"] == "Success":
        builder = item.annotations.builder()
        builder.add(
            annotation_definition=dl.Classification(
                label=json_response["response"]["label"]
            )
        )
        builder.upload()

    print(f"Test final result: {json_response['status']}")


def async_test():
    # TODO: Update item_id and save_locally
    item_id = '64ef71d84cea7f1a3aaef5ad'
    item = dl.items.get(item_id=item_id)
    save_locally = True

    # API requests to the FastAPI Server
    json_response = send_image(item=item, save_locally=save_locally, sync_flag=False)

    for tries in range(3):
        json_response = predict_status(request_id=json_response["request_id"])

        # Upload Annotation
        if json_response["status"] == "Success":
            builder = item.annotations.builder()
            builder.add(
                annotation_definition=dl.Classification(
                    label=json_response["response"]["label"]
                )
            )
            builder.upload()
            break

        time.sleep(5)

    print(f"Test final result: {json_response['status']}")


def main():
    global server_url

    # TODO: Update server host and port
    host = '0.0.0.0'
    port = 9000
    server_url = f"http://{host}:{port}"

    #########
    # Tests #
    #########
    # sync_test()
    async_test()


if __name__ == '__main__':
    main()
