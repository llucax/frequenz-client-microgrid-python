# Frequenz Microgrid API Client Release Notes

## Upgrading

- This release stops using `betterproto` and `grpclib` as backend for gRPC and goes back to using Google's `grpcio` and `protobuf`.

    If your code was using `betterproto` and `grpclib`, it now needs to be ported to use `grpcio` and `protobuf` too. Remember to also remove any `betterproto` and `grpclib` dependencies from your project.

- We are now using base-client v0.6.0.

