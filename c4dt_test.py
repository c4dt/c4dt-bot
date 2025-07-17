# c4dt-test - testing the agent - Licensed under AGPLv3 or later

import asyncio
from common import StdLogger
from agent import answer_message, general_query, get_command, AgCmd, set_weekly_urls, get_weekly_urls, set_personal_interest, get_personal_interest, update_personal_interest, get_weekly

async def test_it():
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

    # await update_personal_interest("ligasser", personal_interest_linus)
    # print(get_personal_interest("ligasser"))

    get_personal_preferences = "what are my personal preferences?"
    # cmd = await get_command("ligasser", get_personal_preferences)
    # print(f"Command is: {cmd}")
    
    # await update_personal_interest("ligasser", get_personal_preferences)
    # print(get_personal_interest("ligasser"))

    # answer = await answer_message("ligasser", get_personal_preferences)
    # print(f"quering for my personal preferences: {answer}")

    # answer = get_weekly("ligasser", ["4", ""])
    # print(answer)

    # print(await answer_message("ligasser", "2 weekly picks"))
    
    # answer = await answer_message("ligasser", personal_interest_linus)
    # print(f"updating personal interests: {answer}")
    
    answer = await answer_message("ligasser", "what are my personal preferences?")
    print(f"quering for my personal preferences: {answer}")

asyncio.run(test_it())