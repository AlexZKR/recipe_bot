# Conversation states for TikTok recipe creation
URL, PROCESSING, CATEGORY, TAGS, SAVE = range(5)

# Messages
TIKTOK_START = "Let's create a recipe from TikTok! Please paste the TikTok share URL (e.g., https://vm.tiktok.com/xxxxx/)"
TIKTOK_URL_INVALID = "That doesn't look like a valid TikTok URL. Please try again with a TikTok share URL."
TIKTOK_PROCESSING = "🔄 Processing your TikTok video... This may take a moment."
TIKTOK_PROCESSING_SUCCESS = "✅ Successfully extracted recipe from TikTok!"
TIKTOK_PROCESSING_ERROR = "❌ Sorry, I couldn't extract a recipe from that TikTok URL. Please check the URL and try again."
TIKTOK_CATEGORY = (
    "What category does this recipe belong to (use keyboard for range of options)?"
)
TIKTOK_CATEGORY_INVALID = (
    "Please select a valid category from the keyboard options provided."
)
TIKTOK_TAGS = (
    "Add tags to your recipe (optional). Select from existing tags or type a new one:"
)
TIKTOK_TAGS_NEW_PROMPT = "Enter the name for your new tag:"
TIKTOK_TAGS_DONE = "Tags added. Saving recipe..."
TIKTOK_SAVE_SUCCESS = "🎉 Recipe saved successfully!"
TIKTOK_CANCEL = "Okay, I've cancelled the process. Your recipe has not been saved."
