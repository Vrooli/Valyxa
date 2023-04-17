"""Shortens text to a specified length"""
TEXT_BREVITY = "Condense the provided text to a length of {{number}} {{type}}, while preserving the core ideas and main points. Ensure the shortened text maintains coherence, readability, and accurately conveys the original message."

"""Expands text to a specified length"""
TEXT_VERBOSITY = "Expand the provided text to a length of {{number}} {{type}}, while maintaining the core ideas and main points. Ensure the lengthened text remains coherent, engaging, and accurately conveys the original message, adding relevant details, examples, or context as needed."

"""Converts text to bullet points"""
TEXT_BULLET_POINT = "Analyze the provided text and extract the most important points and key ideas. Create a concise bullet point summary that captures the essence of the content, maintaining clarity and accuracy while presenting the information in a structured and easily digestible format."

"""Continues writing a text"""
TEXT_CONTINUE = "Continue writing the provided text by generating {{number}} {{type}} that maintain the existing tone, style, and content. Ensure the new {{type}} logically extend the narrative and contribute to the development of the topic or story."

"""Adjust casual/formal tone of text"""
TEXT_FORMALITY = "Modify the provided text to match the desired formality level, with 0 being the most casual and 1 being the most formal. Adjust the tone, vocabulary, sentence structure, and phrasing accordingly to achieve a {{formality_level}} level of formality, while preserving the original message and maintaining readability."

"""Organizes text from unstructured to structured"""
TEXT_ORGANIZE = "Analyze the provided unstructured text and identify key ideas, themes, and relationships. Reorganize the content into a structured format, combining snippets or elements as necessary to create a cohesive, coherent, and easily digestible piece. This may involve turning meeting notes into a summary, rearranging information for better flow, or consolidating related ideas into unified sections."

"""
Changes reading level of text.

Options: 
- Baby
- Preschool
- Kindergarten
- 1st Grade, 2nd Grade, 3rd Grade, 4th Grade, 5th Grade, 6th Grade, 7th Grade, 8th Grade, 9th Grade, 10th Grade, 11th Grade, 12th Grade,
- Undergraduate, Graduate, Post-Graduate
- Professional, Business, Academic
- Adult, College, High School
- Easy, Medium, Hard
- General, Technical, Academic
- Genius, Smart, Average, Dumb
- X IQ
"""
TEXT_READING_LEVEL = "Adjust the provided text to a {{reading_level}} level, modifying vocabulary, sentence structure, complexity, and phrasing while preserving the original message and readability."

"""Explains text as if you are x years old"""
TEXT_EXPLAIN = "Explain the provided text as if you were {{age}} years old, using simple language and clear, concise phrasing. Ensure the explanation is accurate and conveys the original message, while maintaining readability."

"""Change the style of a text"""
TEXT_STYLE = "Rewrite the provided text in the style of {{desired_style}}, emulating the tone, vocabulary, sentence structure, and unique characteristics of the chosen style, while preserving the original message and ensuring readability."