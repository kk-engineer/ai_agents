# AGENT.md 
# Operational Logic
- **Strict Syntax:** You must ONLY respond in the ReAct format.
- **Rule 1:** If a tool is needed: `Thought:` -> `Action:` -> `Action Input:` -> `Observation:`.
- **Rule 2:** If NO tool is needed (e.g., greetings, general questions): `Thought:` -> `Final Answer:`.
- **Formatting:** NEVER provide text outside of the `Final Answer:` or `Thought:` blocks.
- **MacOS Rules:** Use `zsh` compatible commands. Avoid destructive commands like `rm`,`mv` etc.
- **Example:** For system configuration run this multi-command in one action:
  - sw_vers -productVersion; system_profiler SPHardwareDataType | grep -E "Model Name|Chip|Memory"; system_profiler SPDisplaysDataType | grep "Chipset Model"; df -H /System/Volumes/Data | head -n 2; 
system_profiler SPHardwareDataType | grep -E "Total Number of Cores"; system_profiler SPDisplaysDataType | grep -E "Total Number of Cores"
- **Goal:** Try to solve the user's request in as few Actions as possible.

## Observation Analysis
- **STRICT RULE:** Once you receive an `Observation`, you must first check if the answer is inside it. 
- If the data is present, you MUST NOT use a tool again. 
- Immediately move to `Thought: I now have the answer` followed by `Final Answer:`.
- **Never repeat the same search query twice.**