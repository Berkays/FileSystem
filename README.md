## Docker Installation

docker build -t server .

## Docker Run

Change port 10001 for each node

docker run -p 10001:18861 server

## Run Client

Edit host list and mount points in client.py
Edit control backup path in control.py
run python3 client.py