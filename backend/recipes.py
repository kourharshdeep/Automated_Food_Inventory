RECIPES = [
    {
        "name": "Toast / Sandwich",
        "ingredients": ["bread", "butter"],
        "instructions": "Toast the bread slices. Spread butter evenly. Serve warm."
    },
    {
        "name": "Banana Smoothie",
        "ingredients": ["banana", "milk"],
        "instructions": "Blend banana and milk until smooth. Serve chilled."
    },
    {
        "name": "French Toast",
        "ingredients": ["egg", "bread"],
        "instructions": "Whisk egg, dip bread in the mixture. Pan-fry until golden."
    },
    {
        "name": "Stir Fry Veggie Bowl",
        "ingredients": ["carrot", "broccoli"],
        "instructions": "Chop veggies and stir fry with soy sauce for 10 mins. Serve with rice."
    },
    {
        "name": "Apple Salad",
        "ingredients": ["apple"],
        "instructions": "Chop apple into cubes. Toss with a light dressing or eat fresh."
    },
    {
        "name": "Reheated Pizza",
        "ingredients": ["pizza"],
        "instructions": "Reheat pizza in an oven or skillet for a crispy crust. Enjoy!"
    }
]

def suggest_recipes(inventory_items):
    """
    Suggest recipes based on current inventory items.
    """
    inventory_names = [item['item_name'].lower() for item in inventory_items]
    suggestions = []
    
    for recipe in RECIPES:
        # Check if at least one ingredient is in the inventory
        match = any(ing in inventory_names for ing in recipe["ingredients"])
        if match:
            suggestions.append(recipe)
            
    return suggestions
