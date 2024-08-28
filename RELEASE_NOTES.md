# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- This release stops using `betterproto` and `grpclib` as backend for gRPC and goes back to using Google's `grpcio` and `protobuf`.

    If your code was using `betterproto` and `grpclib`, it now needs to be ported to use `grpcio` and `protobuf` too. Remember to also remove any `betterproto` and `grpclib` dependencies from your project.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
