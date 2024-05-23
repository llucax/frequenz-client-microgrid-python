# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- The client is now using [`grpclib`](https://pypi.org/project/grpclib/) to connect to the server instead of [`grpcio`](https://pypi.org/project/grpcio/). You might need to adapt the way you connect to the server in your code, using `grpcio.client.Channel`.
- The client now doesn't raise `grpc.aio.RpcError` exceptions anymore. Instead, it raises `ClientError` exceptions that have the `grpclib.GRPCError` as their `__cause__`. You might need to adapt your error handling code to catch `ClientError` exceptions instead of `grpc.aio.RpcError` exceptions.
- The client now uses protobuf/grpc bindings generated [betterproto](https://github.com/danielgtaylor/python-betterproto) instead of [grpcio](https://pypi.org/project/grpcio/). If you were using the bindings directly, you might need to do some minor adjustments to your code.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

- Fix a leakage of `GrpcStreamBroadcaster` instances.
- The user-passed retry strategy was not properly used by the data streaming methods.
- The client `set_bounds()` method might have not done anything and if it did, errors were not properly raised.
