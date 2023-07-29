# 🙆‍♀️Valyxa: Your Personal Assistant and Co-worker
Valyxa is an autonomous agent designed to work in tandem with [the Vrooli platform][website], acting as a personal assistant and co-worker for Vrooli users. Its primary purpose is to streamline and enhance the user experience on Vrooli by offering personalized suggestions, automating tasks, and collaborating with users to improve productivity and achieve their goals.

Some of Valyxa's features include:
- Intelligent reminders management
- Calendar optimization
- Organization and team automation
- Routine automation and improvement
- Project automation and improvement
- Standards and API implementation
- Smart contract management
- Text manipulation


# 🌟 The Vision
As Vrooli users pursue their goals and work on their projects, Valyxa will be there to support them every step of the way. By intelligently adapting to users' needs and preferences, Valyxa will provide invaluable assistance and collaboration to maximize productivity and efficiency. The key aspects of Valyxa's vision are:

<details>
  <summary><b>Intelligent Reminders Management</b></summary>
  Valyxa will revolutionize how users manage reminders by:  

  * Creating organizations, projects, routines, standards, APIs, etc., to autonomously complete reminders
  * Prioritizing reminders according to user preferences and needs
  * Suggesting new reminders
</details>
<details>
  <summary><b>Calendar Optimization</b></summary>
  Valyxa will optimize users' calendars by:

  * Filling available time with suggested actions
  * Reducing busy time by identifying inefficiencies and automatable tasks
</details>
<details>
  <summary><b>Team and Organization Support</b></summary>
  Valyxa will enhance team and organization dynamics by:

  * Adding bot team members
  * Auto-implementing incomplete routines, projects, etc.
  * Facilitating individual and group chats with bot members
</details>
<details>
  <summary><b>Routine Automation and Improvement</b></summary>
  Valyxa will streamline routines by:

  * Auto-implementing and auto-running routines
  * Suggesting routines to complete next
  * Auto-improving routines by optimizing cost, complexity, and other factors
</details>
<details>
  <summary><b>Project Automation and Improvement</b></summary>
  Valyxa will boost project management by:

  * Auto-implementing and auto-running projects
</details>
<details>
  <summary><b>Standards and API Implementation</b></summary>
  Valyxa will simplify the implementation of standards and APIs by:

  * Auto-implementing and auto-improving standards and APIs based on user preferences and requirements
</details>
<details>
  <summary><b>Smart Contract Management</b></summary>
  Valyxa will empower users to manage smart contracts effectively by:

  * Auto-implementing and auto-improving smart contracts
  * Providing auditing capabilities to ensure contract security and compliance
</details>
<details>
  <summary><b>Text Manipulation</b></summary>
  Valyxa will enable users to effortlessly manipulate freeform text (e.g., notes, descriptions, chat messages) by providing features to:

  * Convert text to bullet points
  * Change reading level
  * Adjust formality
  * Alter length
  * Organize content
  * Summarize information
  * Continue writing
</details>


# 🔑 Why Valyxa?
Valyxa is designed to complement the Vrooli platform, enhancing the user experience and helping users achieve their goals more efficiently. By acting as a personal assistant and co-worker, Valyxa provides the support, automation, and collaboration needed to take productivity to the next level.

## [👩🏼‍💻 Developer setup][setup-guide]
Linked is our guide for setting up all Vrooli repos. This should cover most of the setup needed to run Valyxa. Currently, the only extra step is that you must copy Vrooli's `jwt_pub.pem` and `jwt_priv.pem` (which are auto-generated when you run `setup.sh` in Vrooli) to the root of this repo. These files are used to verify and sign JSON Web Tokens (JWTs) for authentication, which is required to secure chat conversations.

## How it works
1. The user starts a conversation with Valyxa or another bot on Vrooli
2. Vrooli's backend loads that bot's persona configuration (if any), and sends it here, to Valyxa
3. We combine the persona configuration with [start.yml](src/tasks/en/start.yml), and send return `persona.startMessage` to the user
4. The user chats with the bot, and the bot responds. 
    - If the user doesn't ask to do anything specific, the bot will respond without any further configuration
    - If the user's message contains a command contained in the configuration (e.g. `/create note <note description>`), we add the configuration to the message, and send it to ChatGPT to generate a response
    - If the user's message implies a command (e.g. `I want to create a note`), the bot should include the command in its response. We'll then send the command to ChatGPT in a new message to generate a response

## Usage
If not using [Vrooli](https://github.com/Vrooli/Vrooli) or another UI that's already set up to use Valyxa, you can send a POST request to `http://localhost:<PORT_VALYXA>` if testing locally, or `https://<your-domain>` if testing on a Virtual Private Server (VPS). The request must follow this structure:

```json
{
    "key": "<your-api-key>", // Can use API_FOR_VROOLI for uncapped usage. Otherwise, we validate and fetch api information from VROOLI_URL
    "config": "<config>", // Optional configuration if not starting a generic conversation. See `ai_assistant.features.commands.commands` in `start.yml` for options
    "message": "Initial response, or reply in conversation",
    "messageId": <message-id>, // Optional ID if continuing message. Must be continuing the conversation using the same key
    "jwt": "<json-web-token>", // If key is API_FOR_VROOLI, this token ensures that the conversation cannot be accessed by anyone else
}
```

## Testing through OpenAI
You can simulate this program through [ChatGPT](https://chat.openai.com/) or the [OpenAI Playground](https://platform.openai.com/playground) by pasting in configuration prompts directly. Start by copying your desired configuration (e.g. [start.yml](src/tasks/en/start.yml)). 
- If you're using ChatGPT, paste the configuration as the first message, with no other text. It should respond with the `startMessage`, as defined in the configuration. GPT-3.5 tends to add additional text after the message, but this doesn't affect the functionality of the program. 
- If you're using the Playground, you should set the configuration as the system message. Then, manually create the assistant's first message (which should be the `startMessage`). After that, you can create a new message for the user and press "Submit".

Then continue the conversation from there. To simulate what Valyxa does, you'll need to inject task-specific configurations at certain times:
- When the user enters a command (e.g. `/create note <note description>`), you must inject the configuration at the start of the user's message. 
- When the bot enters a command, you must send a new message containing the command.

```

```
Use the guideline below to help me with this task:

<contents_of_text.yml_file>

<your_message>
```

 so that Valyxa is ready to help you create a note. When starting a task without specifying a command (e.g. you enter "I want to create a new note"), the AI should respond with something like:

```
<Command: /create note> Sure! what would you want to create a note about?
```

At the start of your next message, you must provide the [text.yml]() configuration just like before:

```
<contents_of_text.yml_file>

<your_message>
```

### Improving Configuration Prompts
ChatGPT is great at improving configuration prompts. To do so, enter this whenever the AI responds unexpectedly:

```
That is not the response I expected. I wanted you to <your criticism>. Please suggest a new configuration file that might fix this issue.
```

## Measuring prompt size
The shorter prompts are, the longer the AI can remember the conversation before we must re-inject the prompt. We explore ways to reduce the prompt size [here](docs/PromptShrinking.md).

For now, we'll continue to use YAML to design prompts because it's the easiest to read and write. In the future, we may have a compile step that converts this to stringified JSON (without whitespaces) to reduce prompt size.

# 🦜 Multilingual Support
We are actively seeking multilingual speakers to help us translate Valyxa's prompts and documentation to make our platform accessible to a wider audience. If you are a multilingual speaker and would like to contribute by providing translations, please add your language to the `translations` folder and submit a pull request. We will review your contribution and, if approved, merge it into the main repository.

Thank you for your support and for helping us build a more inclusive and diverse Vrooli community!

# 🤝 Join the Team
Valyxa's vision is ambitious, and we could use all the help we can get to bring it to life. If you would like to contribute to Valyxa or Vrooli, please don't hesitate to reach out. Your efforts will be greatly appreciated, and you will play an integral role in building a better future for productivity and collaboration.

### [<img align="center" alt="Website" width="36px" src="./docs/assets/vrooli.png" style="padding-left:5px;padding-right:2px" />][start] [**Let's change the world together!🕊**][start]

[website]: https://vrooli.com
[start]: https://vrooli.com/start
[setup-guide]: https://docs.vrooli.com/setup/getting_started.html
