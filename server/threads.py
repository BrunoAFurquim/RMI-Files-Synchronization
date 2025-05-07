import threading

class RequestThread(threading.Thread):
    def __init__(self, dispatcher, request_data):
        super().__init__()
        self.dispatcher = dispatcher
        self.request_data = request_data
    
    def run(self):
        self.dispatcher.handle_request(self.request_data)