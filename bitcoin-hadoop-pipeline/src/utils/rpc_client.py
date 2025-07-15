import asyncio
import aiohttp
import time
from typing import Any, List, Dict
from utils.config import config
from utils.logger import logger


class RPCClient:
    """
    Async JSON-RPC client for interacting with a Bitcoin full node.

    This client uses aiohttp to perform asynchronous RPC calls to a Bitcoin node.
    It supports context management to properly manage session lifecycle.

    Attributes:
        session (aiohttp.ClientSession): The HTTP session used for making requests.
        logger (logging.Logger): The logger instance for emitting logs.
    """

    def __init__(self):
        """
        Initializes the RPCClient without starting a session.
        The session is initialized upon entering the async context.
        """
        self.session = None
        self.logger = logger

    async def __aenter__(self):
        """
        Asynchronous context manager entry. Initializes the aiohttp session.

        Returns:
            RPCClient: The initialized client instance with an open session.
        """
        self.session = aiohttp.ClientSession()
        self.logger.info("[RPCClient] HTTP session initialized.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asynchronous context manager exit. Closes the aiohttp session.

        Args:
            exc_type: Exception type, if any.
            exc_val: Exception value, if any.
            exc_tb: Traceback, if any.
        """
        self.logger.info("[RPCClient] Closing HTTP session.")
        await self.session.close()
        self.logger.info("[RPCClient] HTTP session closed successfully.")

    async def call(self, method: str, params: List[Any] = []) -> Dict[str, Any]:
        """
        Makes an asynchronous JSON-RPC call to the configured Bitcoin node.

        Args:
            method (str): The RPC method name (e.g., 'getblockcount').
            params (List[Any]): Optional list of parameters for the method.

        Returns:
            Dict[str, Any]: The 'result' field from the JSON-RPC response.

        Raises:
            Exception: Reraises any exceptions encountered during the call.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params,
        }

        self.logger.debug(f"[RPCClient] Preparing RPC call: method={method}, params={params}")

        try:
            start_time = time.perf_counter()
            async with self.session.post(
                config.RPC_URL,
                json=payload,
                auth=aiohttp.BasicAuth(config.RPC_USER, config.RPC_PASSWORD),
            ) as resp:
                duration = time.perf_counter() - start_time
                status = resp.status
                self.logger.info(
                    f"[RPCClient] RPC call '{method}' completed with status={status} in {duration:.3f}s"
                )

                resp.raise_for_status()
                result = await resp.json()

                if "error" in result and result["error"] is not None:
                    self.logger.error(f"[RPCClient] RPC error in method='{method}': {result['error']}")
                    raise RuntimeError(result["error"])

                self.logger.debug(f"[RPCClient] RPC result for method='{method}': success")
                return result["result"]

        except aiohttp.ClientResponseError as e:
            self.logger.error(
                f"[RPCClient] HTTP error for RPC method='{method}': {e.status} {e.message}", exc_info=True
            )
            raise e
        except aiohttp.ClientConnectionError as e:
            self.logger.error(
                f"[RPCClient] Connection error while calling method='{method}': {e}", exc_info=True
            )
            raise e
        except Exception as e:
            self.logger.error(f"[RPCClient] Unhandled exception in RPC call '{method}': {e}", exc_info=True)
            raise


async def main():
    """
    Main entry point for testing the RPCClient.

    Retrieves the current block count from the Bitcoin node.
    """
    try:
        async with RPCClient() as rpc:
            block_count = await rpc.call("getblockcount")
            logger.info(f"[main] Current block count: {block_count}")
            return block_count
    except Exception as e:
        logger.critical(f"[main] RPCClient failed: {e}", exc_info=True)


if __name__ == "__main__":
    count = asyncio.run(main())
    print(count)
