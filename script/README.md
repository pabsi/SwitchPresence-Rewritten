# Nintendo Switch Status script

A Python script that connects to a Nintendo Switch running the SwitchPresence-Rewritten sysmodule and retrieves the currently active title. Outputs a JSON object suitable for use as a sensor (e.g. Home Assistant).

## Requirements

Python 3.6+ (standard library only, no extra dependencies).

## Output

```json
{"state": "on", "id": "0x0100abcd1234ef00", "title": "Some Game Title"}
```

When the Switch is off or unreachable:

```json
{"state": "off", "id": -1, "title": "None"}
```

## Usage

```
python switch_status.py [--switch-ip IP] [--port PORT] [--timeout SECONDS] [--log-level LEVEL]
```

| Argument | Default | Description |
|---|---|---|
| `--switch-ip` | `192.168.1.2` | IP address of the Switch |
| `--port` | `51966` | TCP port the sysmodule listens on |
| `--timeout` | `5` | Connection timeout in seconds |
| `--log-level` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |

## Example

```bash
python switch_status.py --switch-ip 192.168.1.100 --port 51966
```

## Notes

- The Switch must have the SwitchPresence-Rewritten sysmodule running.
- The script retries up to 3 times on transient failures. If the host is unreachable it exits immediately and reports state `off`.
- It works fine on my Nintendo Switch 1 even after long deep sleeps. During deep sleep is reporting the switch as off.
