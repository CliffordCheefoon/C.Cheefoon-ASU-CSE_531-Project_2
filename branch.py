import logging
import os

import grpc
from services.gprc_coms import branch_pb2_grpc
from services.gprc_coms import branch_pb2
from services.gprc_coms.branch_pb2 import branchEventRequest, branchEventResponse           # pylint: disable=no-name-in-module
from services.input_parser.parser import branch_input
from services.universal_data_objects import objects
import jsonpickle



class branch_client_stub:                                                                   # pylint: disable=invalid-name
    """Wrapper for branch metadata and stub pointer"""
    branch_metadata : branch_input
    branch_stub: branch_pb2_grpc.branchEventSenderStub

    def __init__(self, branch_metadata: branch_input, stub):
        self.branch_metadata = branch_metadata
        self.branch_stub = stub



class Branch(branch_pb2_grpc.branchEventSenderServicer):
    """Handler Class for the grpc server"""

    def __init__(
            self,
            branch_data:branch_input,
            branches_inputs: list[branch_input],
            server_log_dir: str):
        # unique ID of the Branch
        self.id = branch_data.id
        # replica of the Branch's balance
        self.balance = branch_data.balance
        # the list of process IDs of the branches
        self.branch_cluster_info : list[branch_input]  = branches_inputs
        # a list of received messages used for debugging purpose
        self.recv_msg = list()
        # iterate the processID of the branches
        self.logical_clock = 1
        # iterate the processID of the branches

        #Setup server logger to file
        server_log_dir = server_log_dir + f"/server-branch-id-{self.id}.txt"
        self.logger = logging.getLogger()
        handler =logging.FileHandler(server_log_dir, mode='w')
        formatter = logging.Formatter(
            fmt=f'branch_id:{self.id} %(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.debug(f"Branch server ID:{self.id} started on port: {branch_data.port}")    # pylint: disable=logging-fstring-interpolation
        self.logger.debug(f"Starting balance: {self.balance}")                                  # pylint: disable=logging-fstring-interpolation

        # the list of Client stubs to communicate with the branches
        self.stub_list:list[branch_client_stub] = self.register_peer_stubs(branches_inputs)

        self.logical_clock_output_dir = f"""tests/output/branches/{branch_data.id}.json"""
        os.makedirs(os.path.dirname("tests/output/branches/"), exist_ok=True)


    def register_peer_stubs(
            self,
            branches_inputs: list[branch_input]
            ) -> list[branch_client_stub]:
        "Creates peer branch stubs"
        branch_clients: list[branch_client_stub] = []

        self.logger.debug(f"{len(branches_inputs)} nodes in network (including self)")          # pylint: disable=logging-fstring-interpolation
        for branch_metadata in branches_inputs:
            if branch_metadata.id != self.id:
                channel = grpc.insecure_channel(f'localhost:{branch_metadata.port}')
                stub = branch_pb2_grpc.branchEventSenderStub(channel)
                branch_clients.append(branch_client_stub(branch_metadata, stub))
        self.logger.debug(f"{len(branch_clients)} peer stubs registered")                       # pylint: disable=logging-fstring-interpolation
        return branch_clients



    def MsgDelivery(self,request, context):
        "The message handler"


        if request.customer_id == self.id:
            self.bump_clock_w_event(
                request.customer_request_id,
                branch_pb2.event_type_enum.Name((request.event_type)),                              # pylint:disable=no-member
                f"event_recv from Customer {request.customer_id}", 
                request.logical_clock
                )
        else:
            self.bump_clock_w_event(
                request.customer_request_id,
                f"propogate_{branch_pb2.event_type_enum.Name((request.event_type))}",                              # pylint:disable=no-member
                f"event_recv from Branch {request.customer_id}", 
                request.logical_clock
                )




        self.logger.debug(f"""Recieved Event: customer_id = {request.customer_id} ||event_id = {request.event_id} || event_type = {branch_pb2.event_type_enum.Name((request.event_type)) } || money = {request.money} || logical_clock = {request.logical_clock} || customer_request_id = {request.customer_request_id}""")  # pylint: disable=logging-fstring-interpolation,no-member

        if request.event_type == branch_pb2.event_type_enum.QUERY:                              # pylint:disable=no-member
            balance = self.Query()
            return branchEventResponse(
                event_id=request.event_id,
                event_type="QUERY",
                money = 0.00,
                balance=balance,
                is_success=True)

        elif request.event_type == branch_pb2.event_type_enum.DEPOSIT:                          # pylint:disable=no-member
            balance, success = self.Deposit(
                request.customer_id,
                request.event_id,
                request.event_type,
                request.money,
                request.customer_request_id)

            return branchEventResponse(
                event_id=request.event_id,
                event_type="DEPOSIT",
                money =request.money,
                balance=balance,
                is_success=success)
        elif request.event_type == branch_pb2.event_type_enum.WITHDRAW:                         # pylint:disable=no-member
            balance, success = self.Withdraw(
                request.customer_id,
                request.event_id,
                request.event_type,
                request.money,
                request.customer_request_id)

            return branchEventResponse(
                event_id=request.event_id,
                event_type="WITHDRAW",
                money = request.money,
                balance=balance,
                is_success=success)

        else:
            raise ValueError("Unexpected Event encountered")

    def Query(self) -> float:                                                                   # pylint:disable=invalid-name
        """"Getter for balance"""
        return self.balance

    def Withdraw(                                                                               # pylint:disable=invalid-name
            self,
            customer_id: int,
            event_id:int,
            event: branch_pb2.event_type_enum,                                                  # pylint:disable=invalid-name,no-member
            money: float,
            customer_request_id : int
            ) -> [float,bool]:
        """Decrease balance"""
        if self.withdraw_op_check(money):
            self.balance =  self.balance - money
            self.logger.debug(f"""event_id: {event_id} change balance to {self.balance}""")     # pylint: disable=logging-fstring-interpolation
            if self.id == customer_id:
                #If the customer_id and the branch_id are the same, then this is the customer's 
                # local branch, we need to propogate the change to other branches
                self.Propogate_Withdraw(customer_id,event_id,event,money, customer_request_id)
            return self.balance, True
        else:
            return self.balance, False

    def Deposit(                                                                                # pylint:disable=invalid-name
            self,
            customer_id: int,
            event_id:int,
            event: branch_pb2.event_type_enum,                                                  # pylint:disable=invalid-name,no-member
            money: float,
            customer_request_id : int
            ) -> [float,bool]:
        """increase balance"""
        self.balance =  self.balance + money
        self.logger.debug(f"""event_id: {event_id} change balance to {self.balance}""")         # pylint: disable=logging-fstring-interpolation
        if self.id == customer_id:
                #If the customer_id and the branch_id are the same, then this is the customer's 
                # local branch, we need to propogate the change to other branches
            self.Propogate_Deposit(customer_id,event_id,event,money, customer_request_id)
        return self.balance, True


    def Propogate_Withdraw(                                                                     # pylint:disable=invalid-name
            self,
            customer_id: int,
            event_id:int,
            event: branch_pb2.event_type_enum,                                                  # pylint:disable=invalid-name,no-member
            money: float,
            customer_request_id : int
            ) -> bool:
        """Propogate Withdraw operation to peer branch servers"""
        broadcast_futures: list = []
        for branch in self.stub_list:

            self.bump_clock_w_event(
                customer_request_id,
                "Propogate_Withdraw",
                f"event_sent to branch {branch.branch_metadata.id}"
                )

            broadcast_futures.append(branch.branch_stub.MsgDelivery.future(
                request = branchEventRequest(
                    customer_id=customer_id,
                    event_id=event_id,
                    event_type= event,
                    money= money,
                    logical_clock=self.logical_clock,
                    customer_request_id=customer_request_id
                    )))
        for future in broadcast_futures:
            future.result()

    def Propogate_Deposit(                                                                      # pylint:disable=invalid-name
            self,
            customer_id: int,
            event_id:int,
            event: branch_pb2.event_type_enum,                                                  # pylint:disable=invalid-name,no-member
            money: float,
            customer_request_id : int
            ) -> bool:
        """Propogate Deposit operation to peer branch servers"""
        broadcast_futures: list = []
        for branch in self.stub_list:

            self.bump_clock_w_event(
                customer_request_id,
                "Propogate_Deposit",
                f"event_sent to branch {branch.branch_metadata.id}"
                )

            broadcast_futures.append(branch.branch_stub.MsgDelivery.future(
                request = branchEventRequest(
                    customer_id=customer_id,
                    event_id=event_id,
                    event_type= event,
                    money= money,
                    logical_clock=self.logical_clock,
                    customer_request_id=customer_request_id
                    )))
        for future in broadcast_futures:
            future.result()

    def withdraw_op_check(self, money: float) -> bool:
        """Check if an withdraw operation is valid """
        if self.balance - money < 0.00:
            return False
        else:
            return True

    def ___bump_clock(self, incoming_clock : int = None):
        """Bumps the internal to the next logical tick"""
        if incoming_clock is None:
            self.logical_clock = self.logical_clock + 1
            return
        self.logical_clock = max(self.logical_clock, incoming_clock) + 1
        return

    def bump_clock_w_event(
            self,
            customer_request_id: int,
            interface: str,
            comment: str,
            incoming_clock: int = None):
        """Bumps the internal to the next logical tick tracking the event"""
        self.___bump_clock(incoming_clock)
        self.write_logical_clock_output(customer_request_id, self.logical_clock, interface, comment)
        #TODO log the event
        return

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
    