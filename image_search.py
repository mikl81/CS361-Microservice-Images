import zmq
import json
from imagedl.modules.sources import GoogleImageClient


#Globals
ZMQ_ADDRESS   = "tcp://*:5555"



def searchImages(query:str, limit:int = 10, dest_dir:str="downloads") -> list:
    """
    Searchs google for the indicated query then returns the results equal to the limit(default 10). 
        Destination directory can be provided, defaults to 'downloads'
    """
    image_client = GoogleImageClient(work_dir = dest_dir)
    image_infos = image_client.search(query, search_limits=limit, num_threadings=5)

    retlist = []
    for i in range(limit):
        retlist.append(image_infos[i])

    return retlist

def downloadImages(query:str, dest_dir:str="downloads", limit:int = 10) -> list:
    """
    Downloads provided query specified to the limit, defaults to 10. 
        Destination directory can also be provided, defaults to 'downloads'
    """
    image_client = GoogleImageClient()
    image_infos = searchImages(query, limit=limit, dest_dir=dest_dir)

    retList = image_client.download(image_infos, num_threadings=5)

    return retList

def pull_paths(image_data:list) -> list:
    """
    Pulls the relative paths for the downloaded files to be passed in ZMQ
    """
    path_list = []

    for i in range(len(image_data)):
        path_list.append(image_data[i]["file_path"])


    return path_list

def run_server():
    """
    Boots the ZMQ server and awaits JSON data from client for image search
    """
    context = zmq.Context()
    socket  = context.socket(zmq.REP)
    socket.bind(ZMQ_ADDRESS)
    print("Server listening on %s", ZMQ_ADDRESS)

    while True:
        #Receive query
        data = socket.recv_json()
        if not data:
            socket.send(b"ERROR:empty_query")
            continue

        query, limit, dest_dir = data["query"], int(data["limit"]), data["dest_dir"]

        if limit is None:
            limit = 10
        if dest_dir is None:
            dest_dir = "downloads"

        results = downloadImages(query, limit=limit, dest_dir=dest_dir)
        payload = {
            "results" : pull_paths(results)
        }
        json_pack = json.dumps(payload)

        socket.send_json(json_pack)


if __name__ == "__main__":
    run_server()