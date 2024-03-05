# Frequenz Microgrid API Client Release Notes

## Summary

This version downgrades the `protobuf` dependency to 4.21.6.

This is the version used in the SDK v1.0.0-rc5, which we imported the code from. If we don't do this we introduce an unnecessary dependency conflict with the SDK.
