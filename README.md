# C.Cheefoon-ASU-CSE_531-Project_2

## Problem Statement
In the given scenario, N number of Customers and N number of bank Branches; Customer X 
submits requests (Deposit, Withdraw or Query) to Branch X. The major challenge: it is required 
that all other Branches be aware of the requests made to keep the balance of all the Branches 
consistent. In this highly distributed system, it is often difficult to keep track of all the processes 
the Distributed system takes, especially how these processes relate to each other. 


## Goal
Using Lamport’s logical clock algorithm, demonstrate the relationship between the processes of 
the Distributed system by implementing a logical clock. The logical clock should display the 
order of events for a given transaction, following the Happens-Before Relation. 


## Cool Achievements
 - Wrote the ```server_spawner``` module that handles the creation, port assignment, management, and termination of gPRC server processes.
 - Implemented branch event propagation asynchronously, significantly reducing the time required for event propagation from O(n) to O(1).


## Setup Process

 - Pull the project using git from: https://github.com/CliffordCheefoon/C.Cheefoon-ASU-CSE_531-Project_2.git

 - (Optional) Create a Python virtual environment, and set your terminal to use this environment. Create a venv: ```python3 -m venv .venv```


 - Install the project dependencies using the command :
```pip install -r .\requirements.txt”```



 - Run the program using the command: ```python ./main.py```

 - Observe the terminal debug logs

 - A file “tests/output/output.json” will be generated with the output. Additionally, 
each branch server outputs its log stream to its log file located in 
“tests/server_out/*”. These files are organized by branch_id 




