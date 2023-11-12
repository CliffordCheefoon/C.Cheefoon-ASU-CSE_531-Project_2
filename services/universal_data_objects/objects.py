class logical_clock_output: # pylint:disable=invalid-name
    """"Data object"""
    def __init__(self, customer_request_id : int, logical_clock: int, interface: str, comment: str):
        self.customer_request_id = customer_request_id
        self.logical_clock = logical_clock
        self.logical_clock = logical_clock
        self.interface = interface
        self.comment = comment

class entity_logical_clock_output: # pylint:disable=invalid-name
    """"Data object"""
    def __init__(self, id: int, type: str, events: list[dict]):
        self.id = id
        self.type = type
        self.events = events
