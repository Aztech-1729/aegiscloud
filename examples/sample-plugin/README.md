# Aegis Sample Plugin - System Diagnostics

This is an example plugin demonstrating how to build tools for Aegis Cloud.

## Building

```bash
cargo build --release
```

## Publishing

```bash
aegis plugin publish
```

## Tools Provided

- `get_uptime` - Get system uptime
- `get_disk_usage` - Get disk usage statistics
- `list_services` - List Windows services (requires approval)
