"""
Start of a prompt for converting reminders to organizations, projects, routines, etc. 
Should be preceded and/or followed by additional information to prompt autonomous agent
"""
REMINDERS_CONVERT = "Examine the given list of reminders and identify their underlying themes or objectives. Convert the reminders into organized structures such as organizations, projects, routines, or other relevant categories. Provide a detailed breakdown of how these reminders can be grouped and transformed to create a more efficient and streamlined system for the user."

"""Order reminders by priority."""
REMINDERS_PRIORITIZE = "Please prioritize the following list of reminders based on urgency, importance, due dates, and the percentage of completed steps (if applicable). Analyze the tasks and provide a prioritized list, considering the significance, time sensitivity, due dates, and progress of each item."

"""Suggest new reminders based on the user's current and previously completed reminders."""
REMINDER_SUGGEST = "Analyze the user's current and previously completed reminders to identify patterns and recurring tasks. Based on this analysis, suggest new relevant reminders that the user might need to consider adding to their list, taking into account their habits and preferences."