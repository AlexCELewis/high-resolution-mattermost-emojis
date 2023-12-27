import glob
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

# Variables to change, you need to download the Mattermost git directory from
# https://github.com/mattermost/mattermost
MATTERMOST_GIT_DIRECTORY = "/home/alexander/Downloads/mattermost-master/"
EMOJI_SAVE_PATH = "./assets/apple/"


def emoji_codepoints_to_emoji(emoji_codepoints: str) -> str:
    """
    Convert Mattermost's hypen seperated hex encoded emoji codepoints into emoji characters.

    Examples:
    1f6b2 to 🚲 (Bicycle)
    270c-1f3fe to ✌🏾 (Victory Hand: Medium-Dark Skin Tone)
    """
    emoji_full = ""
    for codepoint in emoji_codepoints.split("-"):
        codepoint_base_10 = int(codepoint, 16)
        emoji_full += chr(codepoint_base_10)
    return emoji_full


def download_emoji(session: requests.Session, emoji_path: str) -> str:
    emoji = emoji_codepoints_to_emoji(emoji_path)

    emoji_content = requests.get(f"https://emojicdn.elk.sh/{emoji}?style=apple").content

    # Some (12 at time of writing) emojis don't exist for Apple on EmojiCDN
    if emoji_content == b'Emoji exists, but style couldn\xe2\x80\x99t be found':
        assert False, f'Emoji {emoji_path} - {emoji_codepoints_to_emoji(emoji_path)} not found'

    with open(f"{EMOJI_SAVE_PATH}{emoji_path}.png", "wb") as f:
        f.write(emoji_content)

    return emoji_path


mattermost_emoji_directory = (
    MATTERMOST_GIT_DIRECTORY + "webapp/channels/src/images/emoji/"
)

emojis_required = {path.split("/")[-1].split(".")[0] for path in glob.glob(f"{mattermost_emoji_directory}/*.png")}
emojis_stored = {path.split("/")[-1].split(".")[0] for path in glob.glob(f"{EMOJI_SAVE_PATH}*.png")}
# Only download emojis we don't have and not the mattermost specific ones
emojis_to_download = emojis_required - emojis_stored - {"mattermost", "emoji", "emoji-custom"}
number_of_emojis_to_download = len(emojis_to_download)

# Download in one session as it is faster
session = requests.session()

with ThreadPoolExecutor(max_workers=25) as executor:
    future_results = {
        executor.submit(download_emoji, session, emoji_to_download)
        for emoji_to_download in emojis_to_download
    }

    for i, future in enumerate(as_completed(future_results), 1):
        try:
            emoji_path = future.result()
        except Exception as exc:
            print(f"{exc!s:39} {i:4} of {number_of_emojis_to_download}")
        else:
            print(f"Downloaded {emoji_path:28} {i:4} of {number_of_emojis_to_download}")
