## Docker Installation

docker build -t server .

## Docker Run

Change port x for each node

docker run -p x:18861 server

## Run Client

Edit host list and mount points in client.py
Edit control backup path in control.py
run python3 client.py