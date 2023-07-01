from typing import List, Tuple
from javascript import AsyncTask
import time

from utils.skill_utils import BehaviorNode
from utils.mc_utils import get_block_id, get_item_id, McVec3


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


class PlaceCraftingTable(BehaviorNode):
    
    def _init_behavior(self):
        crafting_table = self.bot.findBlock({
            "matching": get_block_id("crafting_table"),
            "maxDistance": 100
        })
        if crafting_table is None:
            crafting_table = None
            for item in self.bot.inventory.items():
                if item.name == "crafting_table":
                    crafting_table = item
                    break
            if crafting_table is not None:
                                
                @AsyncTask(start=True)
                def equip(task):
                    self.bot.equip(crafting_table, "hand")
                
                @AsyncTask(start=True)
                def place(task):
                    self.bot.placeBlock(self.bot.blockAt(self.bot.position), McVec3(0, 1, 0).to_vec3())

    def _get_transitions(self) -> List[Tuple[str, callable]]:
        def handle_place(this, old_block, new_block, *args):
            if new_block.name == "crafting_table":
                self.finish()
        return [("blockPlaced", handle_place)]      


# All names and doc strings for all members of this class will be added to the context.
class ItemSkills:


    class CollectQuantity(BehaviorNode):
        """
        Collects blocks of the specified type and quantity.
        Args:
            block_type (str): The type of block to collect.
            quantity (int): The quantity of new blocks to collect.
        """

        def __init__(self, block_type: str, quantity: int, **kwargs):
            self.block_type = block_type
            self.quantity = quantity
            self.starting_quantity = None
            self.last_quantity = None
            super().__init__(**kwargs)

        def _init_behavior(self) -> None:
            self.starting_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
            self.last_quantity = self.starting_quantity
            print("Current inv", self.starting_quantity)
            collect(self.bot, self.block_type)

        def _get_transitions(self) -> List[Tuple[str, callable]]:
            def handle_collect(this, collector, collected, *args):
                time.sleep(1)
                curr_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
                if curr_quantity - self.starting_quantity >= self.quantity:
                    print("Finished collecting")
                    self.finish()
                elif collector.username == self.bot.entity.username and curr_quantity > self.last_quantity:
                    print("Collected", curr_quantity - self.starting_quantity, "out of", self.quantity)
                    collect(self.bot, self.block_type)

            return [("playerCollect", handle_collect)]


    class CollectUntil(BehaviorNode):
        """
        Collects blocks of the specified type until you have the specified amount.
        Args:
            block_type (str): The type of block to collect.
            quantity (int): The quantity at which to stop collecting.
        """

        def __init__(self, block_type: str, quantity: int, **kwargs):
            self.block_type = block_type
            self.quantity = quantity
            self.starting_quantity = None
            self.last_quantity = None
            super().__init__(**kwargs)

        def _init_behavior(self) -> None:
            if sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type) < self.quantity:
                collect(self.bot, self.block_type)
            else:
                self.finish()

        def _get_transitions(self) -> List[Tuple[str, callable]]:

            def handle_collect(this, collector, collected, *args):
                time.sleep(1)
                curr_quantity = sum(x.count for x in self.bot.inventory.items() if x.name == self.block_type)
                if curr_quantity >= self.quantity:
                    print("Finished collecting")
                    self.finish()
                elif collector.username == self.bot.entity.username:
                    collect(self.bot, self.block_type)
                    
            return [("playerCollect", handle_collect)]


    # class CraftItem(Task):
    #     """
    #     Collects required materials and crafts the specified item.
    #     Args:
    #         item_type (str): The type of item to craft.
    #     """
    #     def __init__(self, bot, item_type: str):
    #         self.item_type = item_type
    #         super().__init__(bot)

    #     @property
    #     def task_id(self):
    #         return "craft_{}".format(self.item_type)
        
    #     def init_task(self) -> None:
    #         crafting_table = self.bot.findBlock({
    #             "matching": get_block_id("crafting_table"),
    #             "maxDistance": 100
    #         })
    #         if crafting_table is None:
    #             crafting_table = None
    #             for item in self.bot.inventory.items():
    #                 if item.name == "crafting_table":
    #                     crafting_table = item
    #                     break
    #             if crafting_table is not None:
                                    
    #                 @AsyncTask(start=True)
    #                 def equip(task):
    #                     self.bot.equip(crafting_table, "hand")
                    
    #                 @AsyncTask(start=True)
    #                 def place(task):
    #                     self.bot.placeBlock(self.bot.blockAt(self.bot.position), McVec3(0, 1, 0).to_vec3())

    #         recipes = self.bot.recipesAll(get_item_id(self.item_type), None, crafting_table)

    #         if len(recipes) == 0:
    #             print("Needs a crafting table")
    #         else:
    #             recipe = recipes[0]  # TODO pick easiest recipe

    #             missing_requirements = []
    #             for req in recipe.ingredients:
    #                 for item in self.bot.inventory.items():
    #                     if item.name == req:
    #                         crafting_table = item
    #                         break


    #             print("Crafting", recipe.result.name)
    #             @AsyncTask(start=True)
    #             def craft(task):
    #                 self.bot.craft(recipe, 1, crafting_table)
    #                 self.finish_task()
