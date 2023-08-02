from typing import List, Tuple
from javascript import AsyncTask
import time

from utils.skill_utils import BehaviorNode, construct_sequence
from utils.mc_utils import get_block_id, get_item_id, McVec3, get_item_type


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
        print("Checking inventory for crafting table")
        crafting_table = None
        for item in self.bot.inventory.items():
            if item.name == "crafting_table":
                crafting_table = item
                break

        if crafting_table is not None:  # TODO test
            print("Placing crafting table")
            @AsyncTask(start=True)
            def equip(task):
                self.bot.equip(crafting_table, "hand")
            
            @AsyncTask(start=True)
            def place(task):
                self.bot.placeBlock(self.bot.blockAt(self.bot.position), McVec3(0, 1, 0).to_vec3())
        
        else:
            print("No crafting table in inventory")
            self.finish()

    def _get_transitions(self) -> List[Tuple[str, callable]]:
        def handle_place(this, old_block, new_block, *args):
            if new_block.name == "crafting_table":
                self.finish()
        return [("blockPlaced", handle_place)]
    

class CraftWithTable(BehaviorNode):
    def __init__(self, item_type: str, item_quantity: int, crafting_table, **kwargs):
        self.item_type = item_type
        self.item_quantity = item_quantity
        self.crafting_table = crafting_table
        super().__init__(**kwargs)
    
    def _init_behavior(self) -> None:
        print("Checking for valid recipes")
        recipes = self.bot.recipesFor(get_item_id(self.item_type), None, 1, self.crafting_table)

        # Need to iterate because recipes is a Proxy object
        started = False
        for recipe in recipes:
            print("Crafting", get_item_type(recipe.result.id))
            @AsyncTask(start=True)
            def craft(task):
                self.bot.craft(recipe, self.item_quantity, self.crafting_table)  # TODO This call times out
            started = True
            break

        if not started:
            print("No valid recipes")
        self.finish()


# All names and doc strings for all members of this class will be added to the context.
class ItemSkills:

    # TODO collect events are not triggered consistently
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


    class CraftItem(BehaviorNode):
        """
        Collects required materials and crafts the specified item.
        Args:
            item_type (str): The type of item to craft.
            item_quantity (int): The quantity of items to craft.
        """
        def __init__(self, item_type: str, item_quantity: int, **kwargs):
            self.item_type = item_type
            self.item_quantity = item_quantity
            self.crafting_table = None
            super().__init__(child=self._build_child, **kwargs)

        def _build_child(self):
            if self.crafting_table is None:
                return construct_sequence([
                    dict(clss=PlaceCraftingTable),
                    dict(clss=CraftWithTable, args=[self.item_type, self.item_quantity, self.crafting_table])
                ], bot=self.bot)
            else:
                return CraftWithTable(self.item_type, self.crafting_table, bot=self.bot)
        
        def _init_behavior(self) -> None:
            print("Looking for crafting table nearby")
            self.crafting_table = self.bot.findBlock({
                "matching": get_block_id("crafting_table"),
                "maxDistance": 100
            })
            if self.crafting_table is None:
                print("No crafting table nearby")
            else:
                print("Found crafting table")
            self.finish()
