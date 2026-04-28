import json
import socket
import struct
import logging
import argparse
import sys
import time
import errno

logger = logging.getLogger(__name__)

# PACKETMAGIC = 0xFFAADD23  # DO NOT CHANGE


# Defines a title packet
class Title:
    def __init__(self, raw_data):
        logger.debug(
            f"Initializing Title object with {len(raw_data)} bytes of raw data"
        )

        unpacker = struct.Struct("2L612s")
        logger.debug("Created struct unpacker with format '2L612s'")

        enc_data = unpacker.unpack(raw_data)
        logger.debug(f"Unpacked data: magic={enc_data[0]:#x}, pid={enc_data[1]}")

        self.magic = int(enc_data[0])
        logger.debug(f"Set magic number to {self.magic:#x}")

        if int(enc_data[1]) == 0:
            logger.info("PID is 0, setting name to 'Home Menu'")
            self.pid = int(enc_data[1])
            self.name = "Home Menu"
        else:
            logger.info(f"PID is {enc_data[1]}, decoding title name")
            self.pid = int(enc_data[1])
            self.name = enc_data[2].decode("utf-8", "ignore").split("\x00")[0]
            logger.debug(f"Decoded title name: '{self.name}'")

        logger.info(f"Title initialized: PID={self.pid}, Name='{self.name}'")


def main():
    logger.info("Starting main function")
    sensorJson = {
        "state": "off",
        "id": -1,
        "title": "None",
    }

    switch_server_address = (args.switch_ip, args.port)
    logger.info(f"Switch server address set to {switch_server_address}")

    logger.debug("Creating TCP socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug("Socket created successfully")

    logger.debug(f"Setting socket timeout to {args.timeout} seconds")
    sock.settimeout(5)  # Initial timeout for connection attempts

    max_retries = 3
    data = b""

    for retry_attempt in range(max_retries):
        try:
            if retry_attempt > 0:
                time.sleep(2)  # Wait before retry
                logger.info(f"Retry attempt {retry_attempt + 1}/{max_retries}")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)

            logger.info(
                f"Attempting to connect to Switch at {args.switch_ip}:{args.port}"
            )
            sock.connect(switch_server_address)
            logger.info("Successfully connected to Switch")

            logger.debug("Receiving data from Switch...")
            data = b""
            sock.settimeout(5)  # Short timeout for recv
            try:
                while True:
                    chunk = sock.recv(128)
                    if not chunk:
                        break
                    data += chunk
                    logger.debug(
                        f"Received chunk of {len(chunk)} bytes, total so far: {len(data)}"
                    )
                    if len(data) >= 620:  # Expecting 628 bytes for a full title packet
                        logger.debug("Received expected amount of data, stopping recv")
                        break
            except socket.timeout:
                logger.debug(
                    f"Recv timeout reached, total data received: {len(data)} bytes"
                )
            logger.info(f"Received {len(data)} bytes total from Switch")

            # If we received data, break out of retry loop
            if len(data) > 0:
                logger.info("Successfully received data")
                break
            else:
                logger.warning(
                    f"Received 0 bytes on attempt {retry_attempt + 1}/{max_retries}"
                )
                if retry_attempt < max_retries - 1:
                    logger.info("Retrying...")
                    continue
                else:
                    logger.error("All retry attempts exhausted, no data received")
                    raise Exception("Failed to receive data after 3 attempts")
        except socket.timeout:
            logger.error(
                f"Connection timed out on attempt {retry_attempt + 1}/{max_retries}"
            )
            if retry_attempt < max_retries - 1:
                continue
            else:
                raise
        except socket.error as e:
            # If it's "No route to host", don't retry - just report as off
            if (
                e.errno == errno.EHOSTUNREACH
                or e.errno == errno.ENETUNREACH
                or e.errno == errno.ECONNREFUSED
            ):
                logger.info(
                    f"No route to host (errno {e.errno}), reporting switch as off"
                )
                break
            logger.warning(
                f"Socket error on attempt {retry_attempt + 1}/{max_retries}: {e}"
            )
            if retry_attempt < max_retries - 1:
                continue
            else:
                raise

    # Only try to parse data if we actually received some
    if len(data) > 0:
        try:
            logger.debug("Creating Title object from received data")
            title = Title(data)
            logger.info(f"Title object created successfully")

            # print(title.name)
            sensorJson = {
                "state": "on",
                "id": str(hex(title.pid)).replace("x", ""),
                "title": title.name.title(),
            }

            logger.info(f"Printed title name: '{title.name}'")

            logger.debug("Closing socket connection")
            sock.close()
            logger.info("Socket closed successfully")

        except (socket.timeout, socket.error) as e:
            logger.error(f"Error occurred: {e}")
            # print("off")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=True)
            # print("off")
    else:
        logger.info("No data received, switch will be reported as off")
        sock.close()

    sensorString = json.dumps(sensorJson)
    print(sensorString)
    logger.info("Main function completed")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Nintendo Switch title monitor")
        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the logging level (default: INFO)",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=5,
            help="Set the connection timeout in seconds (default: 5)",
        )
        parser.add_argument(
            "--switch-ip",
            type=str,
            default="192.168.1.2",
            help="Set the IP address of the Switch (default: 192.168.1.2)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=51966,
            help="Set the TCP port of the Switch (default: 51966). Need 3DSwitchPresence-Rewritten NRO running on the Switch on this port",
        )
        args = parser.parse_args()

        # Configure logging with the specified level
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        logger.info(
            f"Script initialized with SWITCH_IP={args.switch_ip}, TCP_PORT={args.port}, TIMEOUT={args.timeout}, LOG_LEVEL={args.log_level}"
        )
        logger.debug("Script execution started")
        main()
        logger.debug("Script execution finished")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl-C).")
        sys.exit(0)
