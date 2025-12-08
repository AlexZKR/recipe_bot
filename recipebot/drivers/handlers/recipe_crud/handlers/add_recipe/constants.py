# Conversation states for recipe creation
TITLE, INGREDIENTS, STEPS, CATEGORY = range(4)

# Messages
ADD_START = "Let's add a recipe. I will ask for the required info. You can cancel at any time by typing /cancel."
ADD_TITLE = "Provide a title for your recipe"
ADD_INGREDIENTS = "Great! Now provide the ingredients."
ADD_STEPS = "Awesome. Now, the steps to prepare it."
ADD_CATEGORY = (
    "What category does this recipe belong to (use keyboard for range of options)?"
)
ADD_CATEGORY_INVALID = (
    "Please select a valid category from the keyboard options provided."
)
ADD_DONE = "All done! Your recipe has been saved."
ADD_CANCEL = "Okay, I've cancelled the process. Your recipe has not been saved."
