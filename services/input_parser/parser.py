import decimal
import logging
from enum import Enum

class customer_input_interface_enum(Enum):                                          # pylint: disable=invalid-name
    """Enum of customer event types"""
    DEPOSIT = 1
    WITHDRAW = 2
    QUERY = 3

class event:                                                                        # pylint: disable=invalid-name
    """Data Structure representing an event of a customer"""
    def __init__(self,
                customer_request_id: int,
                interface: customer_input_interface_enum,
                money: decimal = None):
        self.customer_request_id : int = customer_request_id
        self.interface : customer_input_interface_enum = interface
        self.money : decimal = money

class customer_input:                                                               # pylint: disable=invalid-name
    """Data Structure representing a Customer in the input file"""

    def __init__(self, id_incoming:int , events: list[event]):
        self.id: int = id_incoming
        self.events: list[event] = events

class branch_input:                                                                 # pylint: disable=invalid-name
    """Data Structure representing a Branch in the input file"""
    port: int = None
    def __init__(self, id_incoming:int , balance: decimal):
        self.id: int = id_incoming
        self.balance: decimal = balance



def get_branches(input_obj, logger : logging.Logger) -> list[branch_input]:
    """Converts generic python object of the input file into a list of Branch Data Structures"""
    input_branches : list[branch_input]  = []

    for obj in input_obj:
        if obj["type"] == "branch":
            logger.debug(f"""found branch-> id:{obj["id"]}, balance:{obj["balance"]} """)
            input_branches.append(branch_input(obj["id"],obj["balance"]))

    return input_branches


def get_customers(input_obj, logger : logging.Logger) -> list[customer_input]:
    """Converts generic python object of the input file into a list of Customer Data Structures"""
    input_customers : list[customer_input]  = []

    for obj in input_obj:
        if obj["type"] == "customer":
            events : list[event] = []

            for event_input in  obj["customer-requests"]:

                event_interface: customer_input_interface_enum
                if event_input["interface"] == "withdraw":
                    event_interface = customer_input_interface_enum.WITHDRAW
                elif event_input["interface"] == "query":
                    event_interface = customer_input_interface_enum.QUERY
                elif event_input["interface"] == "deposit":
                    event_interface = customer_input_interface_enum.DEPOSIT
                else:
                    raise ValueError(
                        f"""An unexpected customer event interface 
                        was encountered: {event_input["interface"]}""")

                logger.debug(f"""found customer event-> customer_id:{obj["id"]}, 
                             event_id:{event_input["customer-request-id"]}, event_interface: {event_input["interface"]},
                             event_money: {event_input.get("money")} """)
                events.append(event(event_input["customer-request-id"],event_interface, event_input.get("money")))

            input_customers.append(customer_input(obj["id"], events))
    return input_customers
