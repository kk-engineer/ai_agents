## Terminal & System Rules
- **OS Context:** Operating on macOS (Apple Silicon).
- **Safety Rail:** No destructive commands (e.g., `rm -rf`, `mv` etc.).
- **System configuration**: to get system config, run this multi-command in one action in terminal:
sw_vers -productVersion; system_profiler SPHardwareDataType | grep -E "Model Name|Chip|Memory"; system_profiler SPDisplaysDataType | grep "Chipset Model"; df -H /System/Volumes/Data | head -n 2; 
system_profiler SPHardwareDataType | grep -E "Total Number of Cores"; system_profiler SPDisplaysDataType | grep -E "Total Number of Cores"
- **Critical - No Installs:** You are 'Strictly Forbidden' from running commands that download, install, or update software (e.g., `brew install`, `pip install`, `curl -O`, `wget`, `npm install`) without explicit, written permission from the user for that specific action.