from agent import answer_message, get_command, AgCmd

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
# assert answer.command == [AgCmd.GENERAL, general]

