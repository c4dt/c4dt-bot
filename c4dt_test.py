import asyncio
from common import StdLogger
from agent import answer_message, get_command, AgCmd, set_weekly_urls, get_weekly_urls, set_personal_interest, get_personal_interest, update_personal_interest, get_weekly

std_log = StdLogger()

# answer = get_command("ligasser", "please create 5 weekly picks for me")
# print(answer)
# assert answer.command == AgCmd.WEEKLY
# assert answer.arguments == ["5"]

# answer = get_command("ligasser", "weekly picks")
# print(answer)
# assert answer.command == AgCmd.WEEKLY
# assert answer.arguments == ["3"]

# answer = get_command("ligasser", "weekly")
# print(answer)
# assert answer.command == AgCmd.WEEKLY
# assert answer.arguments == ["3"]

# answer = get_command("ligasser", "weekly on microsoft security problems")
# print(answer)
# assert answer.command == AgCmd.WEEKLY
# assert answer.arguments == ["3", "microsoft security problems"]

# general = "How do I create a for-loop in Haskell?"
# answer = get_command("ligasser", general)
# print(answer)
# assert answer.command == AgCmd.GENERAL
# assert answer.arguments == [general]

# answer = get_command("ligasser", "urls: https://slashdot.org, https://danu.li")
# print(answer)
# assert answer.command == AgCmd.WEEKLY_URLS
# assert answer.arguments == ["https://slashdot.org", "https://danu.li"]

personal_interest_linus = """I like working on MacOS, mostly because there is a good terminal
                     with a useful shell.
                     Privacy-wise I think that we should move much more to a decentralized, federated
                     model, for example mastodon and matrix.
                     This makes me very critical about the big players like Microsoft, Apple, Google,
                     even though they try to play the 'privacy' game from time to time.
                     """
# answer = get_command("ligasser", personal_interest_linus)
# print(answer)
# assert answer.command == AgCmd.PERSONAL_INTEREST

# update_personal_interest("ligasser", personal_interest_linus)
# print(get_personal_interest("ligasser"))

# answer = get_weekly("ligasser", ["4", ""])
# print(answer)

print(asyncio.run(answer_message("ligasser", "2 weekly picks")))
