async def unix_to_block_height_range(rpc, start_ts: int, end_ts: int):
    """
    Given a time range, return the block height range by binary searching block timestamps.
    """
    async def find_block_by_time(target_ts: int) -> int:
        low, high = 0, await rpc.call("getblockcount")
        while low <= high:
            mid = (low + high) // 2
            hash = await rpc.call("getblockhash", [mid])
            block = await rpc.call("getblock", [hash])
            ts = block["time"]
            if ts < target_ts:
                low = mid + 1
            else:
                high = mid - 1
        return low

    from_height = await find_block_by_time(start_ts)
    to_height = await find_block_by_time(end_ts)
    return from_height, to_height
