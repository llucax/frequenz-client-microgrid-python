# Frequenz Microgrid API Client Release Notes

## Summary

This release migrates to use `betterproto` and `grpclib` instead of `grpcio` and `protobuf` internally. It also stops *leaking* these internal libraries to downstream users. It should now be possible to use the client without having to use `grpclib` or `betterproto` directly.

## Upgrading

- The client now uses a string URL to connect to the server, the `grpc_channel` and `target` arguments are now replaced by `server_url`. The current accepted format is `grpc://hostname[:<port:int=9090>][?ssl=<ssl:bool=false>]`, meaning that the `port` and `ssl` are optional and default to 9090 and `false` respectively. You will have to adapt the way you connect to the server in your code.

- The client is now using [`grpclib`](https://pypi.org/project/grpclib/) to connect to the server instead of [`grpcio`](https://pypi.org/project/grpcio/). You might need to adapt your code if you are using `grpcio` directly.

- The client now doesn't raise `grpc.aio.RpcError` exceptions anymore. Instead, it raises its own exceptions, one per gRPC error status code, all inheriting from `GrpcError`, which in turn inherits from `ClientError` (as any other exception raised by this library in the future). `GrpcError`s have the `grpclib.GRPCError` as their `__cause__`. You might need to adapt your error handling code to catch these specific exceptions instead of `grpc.aio.RpcError`.

   You can also access the underlying `grpclib.GRPCError` using the `grpc_error` attribute for `GrpStatusError` exceptions, but it is discouraged because it makes downstream projects dependant on `grpclib` too

- The client now uses protobuf/grpc bindings generated [betterproto](https://github.com/danielgtaylor/python-betterproto) ([frequenz-microgrid-betterproto](https://github.com/frequenz-floss/frequenz-microgrid-betterproto-python)) instead of [grpcio](https://pypi.org/project/grpcio/) ([frequenz-api-microgrid](https://github.com/frequenz-floss/frequenz-api-microgrid)). If you were using the bindings directly, you might need to do some minor adjustments to your code.

- If an unknown EV charger component state is received, it will now be set to `EVChargerComponentState.UNKNOWN` instead of `EVChargerComponentState.UNSPECIFIED`.

## New Features

- The client now raises more specific exceptions based on the gRPC status code, so you can more easily handle different types of errors.

   For example:

   ```python
   try:
      connections = await client.connections()
   except OperationTimedOut:
      ...
   ```

   instead of:

   ```python
   try:
      connections = await client.connections()
   except grpc.aio.RpcError as e:
      if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
         ...
   ```

- We now expose component errors as part of the streamed component data:

   * `BatteryData.errors`
   * `InverterData.errors`

- We now expose component states as part of the streamed component data:

   * `BatteryData.component_state` and `BatteryData.relay_state`
   * `InverterData.component_state`

- Added the missing `EVChargerComponentState.UNKNOWN` state.

## Bug Fixes

- Fix a leakage of `GrpcStreamBroadcaster` instances.
- The user-passed retry strategy was not properly used by the data streaming methods.
- The client `set_bounds()` method might have not done anything and if it did, errors were not properly raised.
