# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- `ApiClient`:

    * The class was renamed to `MicrogridApiClient`.
    * The `api` attribute was renamed to `stub`.

## New Features

- The client now inherits from `frequenz.client.base.BaseApiClient`, so it provides a few new features, like `disconnect()`ing or using it as a context manager. Please refer to the [`BaseApiClient` documentation](https://frequenz-floss.github.io/frequenz-client-base-python/latest/reference/frequenz/client/base/client/#frequenz.client.base.client.BaseApiClient) for more information on these features.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
