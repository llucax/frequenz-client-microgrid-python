# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- The client now uses a string URL to connect to the server, the `grpc_channel` and `target` arguments are now replaced by `server_url`. The current accepted format is `grpc://hostname[:<port:int=9090>][?ssl=<ssl:bool=false>]`, meaning that the `port` and `ssl` are optional and default to 9090 and `false` respectively. You will have to adapt the way you connect to the server in your code.
- The client is now using [`grpclib`](https://pypi.org/project/grpclib/) to connect to the server instead of [`grpcio`](https://pypi.org/project/grpcio/). You might need to adapt your code if you are using `grpcio` directly.
- The client now doesn't raise `grpc.aio.RpcError` exceptions anymore. Instead, it raises `ClientError` exceptions that have the `grpclib.GRPCError` as their `__cause__`. You might need to adapt your error handling code to catch `ClientError` exceptions instead of `grpc.aio.RpcError` exceptions.
- The client now uses protobuf/grpc bindings generated [betterproto](https://github.com/danielgtaylor/python-betterproto) ([frequenz-microgrid-betterproto](https://github.com/frequenz-floss/frequenz-microgrid-betterproto-python)) instead of [grpcio](https://pypi.org/project/grpcio/) ([frequenz-api-microgrid](https://github.com/frequenz-floss/frequenz-api-microgrid)). If you were using the bindings directly, you might need to do some minor adjustments to your code.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

- Fix a leakage of `GrpcStreamBroadcaster` instances.
- The user-passed retry strategy was not properly used by the data streaming methods.
- The client `set_bounds()` method might have not done anything and if it did, errors were not properly raised.
