# Frequenz Microgrid API Client Release Notes

## Summary

Code import from the [SDK v1.0.0-rc5](https://github.com/frequenz-floss/frequenz-sdk-python/releases/tag/v1.0.0-rc5) release.

## Upgrading

Changes compared to the code in the SDK v1.0.0-rc5 release:

* The `MicrogridGrpcClient` class was renamed to `ApiClient`.

    * The `retry_spec` constructor argument was renamed to `retry_strategy`.

* The `MicrogridApiClient` abstract base class was removed, use `ApiClient` instead.

* The `Connection` class is now a `dataclass` instead of a `NamedTuple`. If you use the tuple-like interface (`connection[0]`, etc.) you should use the named attributes instead or use [`dataclasses.astuple()`](https://docs.python.org/3/library/dataclasses.html#dataclasses.astuple) to convert it to a tuple.
