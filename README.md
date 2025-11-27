# SENVEND Public API

This repository contains public APIs for the SENVEND ecosystem.\
We rely on Protocol Buffers (protobuf) and gRPC to define and implement our APIs.\
To make handling protobuf definitions easier, we use [buf.build](https://buf.build/).\
All protobuf definitions are stored in the [`proto/`](./proto/) directory.

## Local vs Cloud APIs

At the moment, you can choose between two main APIs: Cloud and Local.\
The payloads are almost identical, Could and Local APIs only provide small wrappers around the main datastructures.\\

### Local API

The Local API runs on SENVEND Payment Terminals and can be accessed via your local network.\
You can find the protobuf definitions for the Local API in the [`proto/local/`](./proto/local/) directory.\
The Terminal needs to be connected to the same network as your client application. You can connect it via Ethernet or Wi-Fi.\
Before using the Local API with your terminal, you need to enable and configure it in the terminal settings on [my.senvend.com](https://my.senvend.com).\
By default the API listens on port `11111` without authentication and encryption.

### Cloud API (not released yet)

The Cloud API can be accessed at `api.senvend.com:443`.\
You can find the protobuf definitions for the Cloud API in the [`proto/cloud/`](./proto/cloud/) directory.

## Example clients

We provide example clients for various programming languages to help developers get started quickly.
Take a look at the [`clients/`](./clients/) directory for more information.

### Regenerate clients

You can use [./gen.sh](./gen.sh) to regenerate the example clients after making changes to the protobuf definitions.

## Buf schema registry

All definitions in this repository are published to the [SENVEND schema registry on buf.build](https://buf.build/senvend/senvend-public).\
This means you can use them as dependencies in your [buf.build](https://buf.build/) projects for advanced use cases.
