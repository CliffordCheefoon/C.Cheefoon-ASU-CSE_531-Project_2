# C.Cheefoon-ASU-CSE_531-Project_2
## TO-DO: THIS IS THE README FOR PROJECT 1, THIS NEEDS TO GET REWRITTEN

## Problem Statement
In the given scenario, N number of Customers and N number of bank Branches; Customer X submits requests (Deposit, Withdraw or Query) to Branch X. The major: it is required that all other Branches be aware of the requests made to keep the balance of all the Branches consistent.

## Goal
Using Remote Procedure Call’s communication protocol (more specifically gRPC), design and implement a Distributed System in Python. This system should accommodate any number of Customers with any number of events, and any number of Branches while maintaining replication transparency. That is: each Branch’s balance should remain consistent with all other Branches as events occur anywhere in the Branch network.

## Cool Achievements
 - Wrote the ```server_spawner``` module that handles the creation, port assignment, management, and termination of gPRC server processes.
 - Implemented branch event propagation asynchronously, significantly reducing the time required for event propagation from O(n) to O(1).


## Setup Process

 - Pull the project using git from: https://github.com/CliffordCheefoon/C.Cheefoon-ASU-CSE_531-Project_1.git

 - (Optional) Create a Python virtual environment, and set your terminal to use this environment. Create a venv: ```python3 -m venv .venv```


 - Install the project dependencies using the command :
```pip install -r .\requirements.txt”```

 - (Optional) In the main.py file, there is a configuration variable “TEST_INPUT_FILE”. You can modify this to specify which test case you would like to run. Options include:
   - “tests/test_case_50.json” (50 Branch test case)(default)
   - “tests/test_case_100.json” (100 branch test case)
   - “tests/sample_input.json” (Project example test case)

 - Run the program using the command: ```python ./main.py```

 - Observe the terminal debug logs

 - 7.	A file “tests/output/output.json” will be generated with the output. Additionally, each branch server outputs its log stream to its log file located in “tests/server_out/*”. These files are organized by branch_id




