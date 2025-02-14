#!/usr/bin/env python
"""a demonstration of how Bitcoin mining works"""
# pylint: disable=invalid-name

import time
import hashlib
import logging
from typing import List, Optional

from rich.logging import RichHandler
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


class Block:
    """a block in the blockchain"""
    def __init__(self, index, nonce, previous_hash):
        self.index = index
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.timestamp = time.time()

    @property
    def hash(self):
        """hash of the block"""
        sha = hashlib.sha256()
        sha.update(
            str(self.index).encode("utf-8")
            + str(self.timestamp).encode("utf-8")
            + str(self.nonce).encode("utf-8")
            + str(self.previous_hash).encode("utf-8")
        )
        return sha.hexdigest()

    @property
    def difficulty(self) -> int:
        """number of leading zeros in the hash"""
        return len(self.hash) - len(self.hash.lstrip("0"))


class Blockchain:
    """a simple blockchain"""
    def __init__(self, target_seconds_per_block: int):
        self.__chain: List[Block] = [Block(0, 0, 0)]
        self.target_seconds_per_block = target_seconds_per_block

    @property
    def difficulty(self) -> int:
        """difficulty of the next block"""
        if len(self.__chain) < 3:
            return 1

        avg_time_to_mine = (
            (self.last_block.timestamp - self.__chain[-2].timestamp)
            +
            (self.__chain[-2].timestamp - self.__chain[-3].timestamp)
        ) / 2

        if avg_time_to_mine < (self.target_seconds_per_block * 0.5):
            return self.last_block.difficulty + 1
        elif avg_time_to_mine > (self.target_seconds_per_block * 1.5):
            return self.last_block.difficulty - 1
        return self.last_block.difficulty

    @property
    def last_block(self) -> Block:
        """last block in the chain"""
        return self.__chain[-1]

    def to_table(self, new_block: Optional[Block]) -> Table:
        """output the blockchain as a table"""
        table = Table()
        table.add_column("Block", style="cyan")
        table.add_column("Nonce", style="magenta")
        table.add_column("Hash", style="green")
        for block_num, block in enumerate(self.__chain):
            table.add_row(
                str(block_num),
                str(block.nonce),
                block.hash
            )
        if new_block:
            table.add_row(str(len(self.__chain)), str(new_block.nonce), new_block.hash)
        table.caption = "Difficulty: " + str(self.difficulty)
        return table

    def mine(self, live_: Live) -> str:
        """mine a block"""
        prefix_str = '0' * self.difficulty
        nonce = 0

        while True:
            proposed_block = Block(
                index=len(self.__chain),
                nonce=nonce,
                previous_hash=self.last_block.hash
            )
            live_.update(self.to_table(proposed_block))
            if proposed_block.hash.startswith(prefix_str):
                self.__chain.append(proposed_block)
                return proposed_block.hash
            nonce += 1


if __name__ == '__main__':
    chain = Blockchain(target_seconds_per_block=10)

    current_hash = chain.last_block.hash

    with Live(chain.to_table(None), refresh_per_second=4) as live:
        while True:
            current_hash = chain.mine(live)
