# Dependecies

* Docker
* Python >=3.4
* Rpyc package (pip install rpyc)
* Fusepy package (pip install fusepy)

# Docker Installation

Use docker to build node container.

Execute `docker build -t server . ` in docker folder.

# Docker Run

Spawn multiple instance of node.<br>
Change port X for each instance.

Execute `docker run -p X:18861 server` in docker folder.

# Run Client

Execute client<br> `python3 client.py [-c] [-r] [-v] [-p] [--hosts] [--clear]`<br> or<br>
`python3 client.py [-c] [-r] [-v] [-p] [--hosts] [--clear]` in project folder.

## Parameters

| Short        | Long           | Description  |
| ------------ |:--------------:| ------------ |
| -c      | --control | Location of the control layer backup file |
| -v      | --virtual | Virtual filesystem mount location |
| -r      | --real | Physical mount location for virtual filesystem |
| -p      | --port | Port setting for the rpc connections. Usually 18861 |
| None      | --clear | If 1, clear control layer backup file at start. |
| None      | --hosts | Location of the control layer backup file |

## Commands

Commands can be issued in client console.<br>
Form: __Command__-__Parameter__

| Command        | Parameter    | Description        | Example  |
| ------------ | -------------- | -------------- | ------------ |
| shutdown      | Host Ip | Sends a shutdown signal to __X__ | *shutdown-172.17.0.2*