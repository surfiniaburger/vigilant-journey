
# Things I learned while testing pilot

- The `google-generativeai` library has a dependency on `pydantic`. A recent update in `pydantic` has introduced a deprecation warning related to `@model_validator`. This warning can be safely ignored for now, but the `google-generativeai` library will need to be updated eventually.

- The `Session` object from the ADK has been updated. It now uses an `id` field instead of `session_id` and no longer has a `metadata` field or allows for arbitrary extra fields.

- When testing asynchronous methods that have been mocked, it is important to use `AsyncMock` to ensure that the mocks behave correctly in an asynchronous environment.

- When a method is a no-op, tests should assert that the underlying methods are *not* called, rather than asserting that they *are* called.
