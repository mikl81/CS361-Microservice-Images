import os
import zmq
from imagedl.modules.sources import GoogleImageClient


#Globals
ZMQ_ADDRESS   = "tcp://*:5555"



def searchImages(query:str, limit:int = 10, dest_dir:str="downloads") -> list:
    """Searchs google for the indicated query then returns the results equal to the limit(default 10). 
        Destination directory can be provided, defaults to downloads
    """
    image_client = GoogleImageClient(work_dir = dest_dir)
    image_infos = image_client.search(query, search_limits=limit, num_threadings=5)

    retlist = []
    for i in range(limit):
        retlist.append(image_infos[i])

    return retlist

def downloadImages(query:str, dest_dir:str="downloads", limit:int = 10) -> list:

    image_client = GoogleImageClient()
    image_infos = searchImages(query, limit=limit, dest_dir=dest_dir)

    retList = image_client.download(image_infos, num_threadings=5)

    return retList

def pull_paths(image_data:list) -> list:
    path_list = []

    for i in range(len(image_data)):
        path_list.append(image_data[i]["file_path"])


    return path_list

def run_server():
    context = zmq.Context()
    socket  = context.socket(zmq.REP)
    socket.bind(ZMQ_ADDRESS)
    print("Server listening on %s", ZMQ_ADDRESS)

   
    while True:
        #Receive query
        raw = socket.recv()
        query = raw.decode("utf-8").strip()
        print("Received query: %r", query)

        if not query:
            socket.send(b"ERROR:empty_query")
            continue

        #Search
        # # image_url = search_google_images(query)
        # if image_url is None:
        #     socket.send(b"ERROR:no_results")
        #     continue

        # print("Top result URL: %s", image_url)

        # # Fetch image
        # image_bytes = fetch_image_bytes(image_url)
        # if image_bytes is None:
        #     socket.send(b"ERROR:fetch_failed")
        #     continue

        # #Reply with raw image bytes
        # print("Sending image (%d bytes)", len(image_bytes))
        # socket.send(image_bytes)


if __name__ == "__main__":
    #run_server()
    results = downloadImages("mountains", limit=1)
    print(pull_paths(results))