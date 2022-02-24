import random


#Loot callbacks! These functions are considered private
def __nothing():
    print("Nothing\n")

def __bond():
    print("Bond\n")

def __discXP():
    print("Disc XP\n")

def __extraBump():
    print("Extra bump!\n")

loot = [(20, __nothing), (1, __bond), (10, __discXP), (5, __extraBump)]

def rollLoot(dm):
    weights, loots = zip(*loot)
    bigloot = random.choices(loots, weights, k=1)
    print(f"User {dm.user} has received loot:")
    bigloot[0]()
    
