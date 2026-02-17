# TODO: :|
# import os
#
# from ...content.content import Content
# from ...content.placeholders import ContentPlaceholder
# from ...content.placeholders import PlaceholderContent
#
#
# ##
#
#
# class CodeAgentSystemPromptEnvironmentPlaceholder(ContentPlaceholder):
#     pass
#
#
# CODE_AGENT_SYSTEM_PROMPT: Content = [
#     """\
#     You are an interactive assistant specializing in programming tasks.
#
#     Your goal is to assist the user by accomplishing the tasks and answering the questions given to you by the user
#     using your available tools.
#
#     <environment>\
#     """,
#     PlaceholderContent(CodeAgentSystemPromptEnvironmentPlaceholder),
#     """\
#     </environment>
#     """,
# ]
#
#
# def build_code_agent_system_prompt_environment() -> Content:
#     return f"""\
#     Working Directory: {os.getcwd()}
#     """


CODE_AGENT_SYSTEM_PROMPT = """
You are an interactive assistant specializing in programming tasks.

Your goal is to assist the user by accomplishing the tasks and answering the questions given to you by the user using
your available tools.
"""
