### MQTT Web API

## A simple API for connecting a web application with an MQTT broker.

# The main idea of this project is to make it possible to communicate with MQTT devices from a web application using HTTP and WebSockets.

# Features
Connects to an MQTT broker
Subscribe to MQTT topics
Publish messages to MQTT topics
Receive MQTT messages through WebSockets
Simple REST API
Configuration using environment variables
Docker support
Built with FastAPI

# Requirements:
Python 3.12
FastAPI
Uvicorn
Paho MQTT
WebSockets
Pydantic
Docker


## How it works

The application works as a bridge between a web application and an MQTT broker.

Web Application  -> HTTP / WebSocket -> MQTT Web API -> MQTT Broker -> MQTT Devices

The API connects to the MQTT broker and can handle messages between the broker and web clients.

Requirements:
