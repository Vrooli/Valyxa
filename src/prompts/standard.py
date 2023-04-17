from gettext import gettext as _

"""Build a standard based on a title and description"""
STANDARD_FROM_TITLE_DESCRIPTION = _("TODO23")

"""Complete a partially built standard"""
STANDARD_COMPLETE = _("TODO24")

"""Improve an existing standard"""
STANDARD_IMPROVE = _("TODO25")

"""Criticize a standard based on its title, description, and other info"""
STANDARD_CRITICIZE = _("Review the {{standard_type}} standard used on this site, which is utilized to generate input components for completing routines, as well as defining the types of data expected as input and output for routines, API calls, smart contracts, and more. Provide constructive feedback on the standard's design, usability, consistency, and overall effectiveness. Offer recommendations for improvements to enhance the standard's flexibility, maintainability, and scalability, ensuring optimal integration and functionality across various use cases.")

"""Start a conversation for building an optimal LLM prompt (prompts are a type of standard)"""
STANDARD_PROMPT_PROMPT = _("You are a prompt generation robot named Valyxa. You need to gather information about the users goals, objectives, examples of the preferred output, and any other relevant contextual information. The prompt should include all of the necessary information that was provided to you. Ask follow up questions to the user until you are confident you can produce an optimal prompt. Your return should be formatted clearly and optimized for ChatGPT interactions. Start by asking the user the goals, desired output, and any additional information you may need.")