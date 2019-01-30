# Classes for receiving and sending messages
import falcon


class Messages:

    # Get method returns all message descriptions
    def on_get(self, req, resp):
        pass


class Message:

    def on_get(self, req, resp):
        pass

    # Submit EDI file
    def on_put(self, req, resp):
        pass
