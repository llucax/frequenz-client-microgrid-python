# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- The client is now using [`grpclib`](https://pypi.org/project/grpclib/) to connect to the server instead of [`grpcio`](https://pypi.org/project/grpcio/). You might need to adapt the way you connect to the server in your code, using `grpcio.client.Channel` and catching `grpcio.GRPCError` exceptions.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

- Fix a leakage of `GrpcStreamBroadcaster` instances.
- The user-passed retry strategy was not properly used by the data streaming methods.
