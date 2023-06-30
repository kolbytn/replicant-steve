from typing import List, Tuple
from javascript import AsyncTask
import time

from utils.skill_utils import Task
from utils.mc_utils import get_block_id


def collect(bot, block_type: str):
    max_dist = 100

    block = get_block_id(block_type)
    print("Mining block", block.name)

    if block is None:
        bot.chat("I don't know what " + block_type + " is!")

    else:
        target = bot.findBlock({
            "matching": block.id,
            "maxDistance": max_dist
        })
        @AsyncTask(start=True)
        def mine(task):
            bot.collectBlock.collect(target)


class ItemSkills:


    class CollectQuantity(Task):
        """
        Collects blocks of the specified type and quantity.
        Args:
            block_type (str): The type of block to collect.
            quantity (int): The quantity of new blocks to collect.
        """

        def __init__(self, bot, block_type: str, quantity: int):
            self.block_type = block_type
            self.quantity = quantity
            self.starting_quantity = None
            self.last_quantity = None
            super().__init__(bot)

        @property
        def task_id(self):
            return "collect_{}_{}".format(self.quantity, self.block_type)

        def init_task(self) -> None:
            self.starting_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
            self.last_quantity = self.starting_quantity
            print("Current inv", self.starting_quantity)
            collect(self.bot, self.block_type)

        def get_listeners(self) -> List[Tuple[str, callable]]:
            def handle_collect(this, collector, collected, *args):
                time.sleep(1)
                curr_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
                if curr_quantity - self.starting_quantity >= self.quantity:
                    print("Finished collecting")
                    self.finish_task()
                elif collector.username == self.bot.entity.username and curr_quantity > self.last_quantity:
                    print("Collected", curr_quantity - self.starting_quantity, "out of", self.quantity)
                    collect(self.bot, self.block_type)

            return [("playerCollect", handle_collect)]


    class CollectUntil(Task):
        """
        Collects blocks of the specified type until you have the specified amount.
        Args:
            block_type (str): The type of block to collect.
            quantity (int): The quantity at which to stop collecting.
        """

        def __init__(self, bot, block_type: str, quantity: int):
            self.block_type = block_type
            self.quantity = quantity
            self.starting_quantity = None
            self.last_quantity = None
            super().__init__(bot)

        @property
        def task_id(self):
            return "collect_until_{}_{}".format(self.quantity, self.block_type)

        def init_task(self) -> None:
            if sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type) < self.quantity:
                collect(self.bot, self.block_type)

        def get_listeners(self) -> List[Tuple[str, callable]]:

            def handle_collect(this, collector, collected, *args):
                time.sleep(1)
                curr_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
                if curr_quantity >= self.quantity:
                    print("Finished collecting")
                    self.bot.removeListener("playerCollect", handle_collect)
                elif collector.username == self.bot.entity.username:
                    collect(self.bot, self.block_type)
                    
            if sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type) < self.quantity:
                return [("playerCollect", handle_collect)]
            else:
                return []
