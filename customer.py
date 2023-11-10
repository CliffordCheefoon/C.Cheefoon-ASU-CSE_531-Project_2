import os
import grpc
import jsonpickle
from branch import branch_client_stub
from services.gprc_coms import branch_pb2_grpc
from services.gprc_coms import branch_pb2
from services.gprc_coms.branch_pb2 import branchEventRequest, branchEventResponse                       # pylint: disable=no-name-in-module
from services.universal_data_objects import objects
from services.input_parser.parser import branch_input, event


class event_mutate_response:                                                                           # pylint: disable=invalid-name
    """Data Representation Class: Customer events that mutate the balance"""
    def __init__(self, interface: str, result ):
        self.interface = interface
        self.result = result

class event_query_response:                                                                           # pylint: disable=invalid-name
    """Data Representation Class: Customer Query"""
    def __init__(self, interface: str, result ):
        self.interface = interface
        self.balance = result

class customer_response:                                                                        # pylint: disable=invalid-name
    """Data Representation Class: Customer with events"""
    def __init__(self, incoming_id : int , recv : list):
        self.id = incoming_id
        self.recv = recv

class Customer:
    """A customer with it's own GRPC stub to it's own Branch Server"""
    events: list[event]
    def __init__(self, id: int, branch_metadata : branch_input):                                # pylint: disable=redefined-builtin
        # unique ID of the Customer
        self.id = id
        self.logical_clock_output_dir = f"""tests/output/customers/{id}.json"""
        os.makedirs(os.path.dirname("tests/output/customers/"), exist_ok=True)
        # a list of received messages used for debugging purpose
        self.recvMsg: list = []                                                 # pylint: disable=invalid-name
        # pointer for the stub
        self.stub = self.createStub(branch_metadata)
        self.logical_clock = 1

    def soft_reset(self):
        """removes previous recv_msg without removing local branch stub, 
        use for cases were a Customer has more than one set of events to perform."""
        self.recvMsg = list()

    def createStub(self, branch_metadata : branch_input) -> branch_client_stub:                 # pylint: disable=invalid-name
        """Creates an object with the branch metadata and stub pointer"""
        channel = grpc.insecure_channel(f'localhost:{branch_metadata.port}')
        stub = branch_pb2_grpc.branchEventSenderStub(channel)
        return branch_client_stub(branch_metadata, stub)


    def executeEvents(self,events: list[event]):                                                # pylint: disable=invalid-name
        """Execute events from a customer. This is not all events for that customer, 
        just a subset that occurs at the same time"""


        for incoming_event in events:
            response: branchEventResponse = self.stub.branch_stub.MsgDelivery(
                request = branchEventRequest(
                    customer_id=self.id,
                    event_id=incoming_event.customer_request_id,
                    event_type= incoming_event.interface.name,
                    money= incoming_event.money,
                    logical_clock=self.logical_clock,
                    customer_request_id=incoming_event.customer_request_id))
            
            
            self.write_logical_clock_output(
                response.event_id,
                self.logical_clock,
                incoming_event.interface.name,
                f"event_sent from customer {self.id}"
                )
            
            self.___bump_clock()

            if response.event_type ==  branch_pb2.event_type_enum.QUERY:                        # pylint:disable=no-member
                self.recvMsg.append(event_query_response("query", response.balance))

            elif response.event_type ==  branch_pb2.event_type_enum.DEPOSIT:                    # pylint:disable=no-member
                success_str : str
                if response.is_success is True:
                    success_str = "success"
                else:
                    success_str = "failed"

                self.recvMsg.append(event_mutate_response("deposit", success_str))

            elif response.event_type ==  branch_pb2.event_type_enum.WITHDRAW:                   # pylint:disable=no-member
                success_str : str
                if response.is_success is True:
                    success_str = "success"
                else:
                    success_str = "failed"

                self.recvMsg.append(event_mutate_response("withdraw", success_str))
            else:
                raise ValueError("Encountered an unexpected event_type")

    def get_customer_log(self) -> customer_response:
        "create a custom response object for output"
        return customer_response(self.id, self.recvMsg)

    def write_logical_clock_output(
            self,
            customer_request_id: int,
            logical_clock: int,
            interface: str,
            comment: str
            ):
        """writes the logical clock output to file"""
        interface = str.lower(interface)
        data: objects.logical_clock_output = objects.logical_clock_output(
            customer_request_id,
            logical_clock,
            interface, comment)
        with open(self.logical_clock_output_dir, "a", encoding="UTF8") as outfile:
            outfile.write(jsonpickle.encode(
                data,
                unpicklable=False) + "\n")

    def ___bump_clock(self, incoming_clock : int = None):
        """Bumps the internal to the next logical tick"""
        if incoming_clock is None:
            self.logical_clock = self.logical_clock + 1
            return
        self.logical_clock = max(self.logical_clock, incoming_clock) + 1
        return
