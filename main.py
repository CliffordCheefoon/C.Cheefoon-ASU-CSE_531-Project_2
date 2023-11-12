import json
import logging
import time
from customer import Customer, customer_response
from services.input_parser.parser import get_branches, get_customers
from services.server_spawner.manager import branch_server_spawn_manager
import os
import glob
import jsonpickle

from services.universal_data_objects.objects import entity_logical_clock_output

#######################config####################################
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
PORT_OFFSET : int = 50000
TEST_INPUT_FILE : str = """tests/sample_input.json"""
TEST_OUTPUT_FILE: str = """tests/output/output.json"""
BRANCH_SERVER_LOG_DIR :str = """tests/server_out_logs/"""
################################################################


def aggregate_output():
    """Aggregated the logical clock output of all the processes
    and transforms them into the final output format"""
    BRANCH_FILES_DIR = "tests/output/branches/"
    CUSTOMER_FILES_DIR = "tests/output/customers/"
    FINAL_OUTPUT_FILE = "tests/output/output.json"

    os.remove(FINAL_OUTPUT_FILE)

    with open(FINAL_OUTPUT_FILE, 'a') as output_stream:
        customer_logical_output_list = grab_output(CUSTOMER_FILES_DIR, "customer")
        branch_logical_output_list = grab_output(BRANCH_FILES_DIR, "branch")


        output_stream.write("//PART 1  \n") 
        output_stream.write(jsonpickle.encode(
            customer_logical_output_list,
            unpicklable=False) + "\n")

        output_stream.write("//PART 2  \n") 
        output_stream.write(jsonpickle.encode(
            branch_logical_output_list,
            unpicklable=False) + "\n")


        raw_events : list[dict] = []

        for item in customer_logical_output_list:
            for event in item.events:
                raw_events.append(event)

        for item in branch_logical_output_list:
            for event in item.events:
                raw_events.append(event)


        raw_events = sorted(
            raw_events,
            key=lambda k: (k['customer_request_id'], k['logical_clock']))

        output_stream.write("//PART 3  \n") 
        output_stream.write(jsonpickle.encode(
            raw_events,
            unpicklable=False) + "\n")



def grab_output(INPUT_FILES_DIR, type) -> list[entity_logical_clock_output]:
    """Converts all logical clock output files in a directory in 
    a list of event datatypes"""
    input_files = glob.glob(f'{INPUT_FILES_DIR}*')
    logical_clock_output_list : list[entity_logical_clock_output] = []

    for input_file in input_files:
        id = input_file.replace("""\\""", "/").split("/")[-1].split(".")[0]
        with open(input_file, 'r') as input_stream:
            lines =input_stream.readlines()
            events : list = []
            for line in lines:
                events.append(jsonpickle.decode(line))
            logical_clock_output_list.append(entity_logical_clock_output(id, type, events))
    return logical_clock_output_list


def main(input_file_dir : str):
    #Create directories for output files
    os.makedirs(os.path.dirname(TEST_OUTPUT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(BRANCH_SERVER_LOG_DIR), exist_ok=True)

    #Clear previous run branch server logs
    files = glob.glob(f'{BRANCH_SERVER_LOG_DIR}*')
    for f in files:
        os.remove(f)

    #Clear previous logical clock output files (Customers)
    files = glob.glob('tests/output/customers/*')
    for f in files:
        os.remove(f)


    #Clear previous logical clock output files (Branches)
    files = glob.glob('tests/output/branches/*')
    for f in files:
        os.remove(f)

    input_json = json.load( open(input_file_dir, 'r', encoding="UTF8"))
    branches_inputs = get_branches(input_json, logging.getLogger())
    customer_inputs = get_customers(input_json, logging.getLogger())
    branch_server_spawn_manager_instance = branch_server_spawn_manager()
    branch_server_spawn_manager_instance.assign_ports(branches_inputs, PORT_OFFSET)
    for branches_input in branches_inputs:
        branch_server_spawn_manager_instance.spawn_server(
            branches_input, branches_inputs, BRANCH_SERVER_LOG_DIR )

    time.sleep(2)

    Customers : list[Customer] = []

    for branch in branches_inputs:
        Customers.append(Customer(branch.id, branch))


    for customer_input in customer_inputs:
        for customer in Customers:
            if customer_input.id == customer.id:
                customer.soft_reset()
                customer.executeEvents(customer_input.events)
                break


    branch_server_spawn_manager_instance.terminate_servers()
    aggregate_output()





if __name__ == "__main__":
    main(TEST_INPUT_FILE)
