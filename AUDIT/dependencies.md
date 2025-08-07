# Dependency Report

| Module | External Imports | Notes |
| --- | --- | --- |
| evolution.common.kafka_utils | kafka-python | used for Kafka messaging |
| tools.ecosystem.library.foundation.code_executor | tools.ecosystem.protocols.native_bridge | internal bridge |
| tests.test_garbage_flag | jsonschema | ModuleNotFoundError during tests |
| tests.* (many) | asyncio | async tests require pytest-asyncio plugin |
