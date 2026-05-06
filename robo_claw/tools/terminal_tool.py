from langchain_community.tools import ShellTool


def validate_command(cmd: str):
    # Ensure we are working with a string
    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    forbidden = ["rm", "mv", "sudo", "chmod", "delete"]
    # Check for forbidden commands in a case-insensitive way
    if any(f in cmd.lower() for f in forbidden):
        raise ValueError(f"Unsafe command detected: {cmd}")
    return cmd


class SafeShellTool(ShellTool):
    def _run(self, command):
        # ✅ Handle if the input is a list (fixes the 'list' object has no attribute 'lower' error)
        if isinstance(command, list):
            command = " ".join(command)

        # Clean potential brackets or quotes from the LLM
        clean_command = str(command).strip("[]'\" ")
        if clean_command.count('"') % 2 != 0:
            clean_command += '"'

        # Validate BEFORE execution
        command = validate_command(clean_command)

        print(f"[SAFE EXEC] {command}")
        return super()._run(command)


def get_terminal_tool():
    shell_tool = SafeShellTool()
    shell_tool.description = (
        "A tool for macOS system diagnostics. Input must be a raw bash command string. "
        "Use 'sw_vers -productVersion' for the macOS version. "
        "Use 'system_profiler SPHardwareDataType | grep -E \"Model Name|Chip|Memory\"' for CPU and RAM. "
        "Use 'system_profiler SPDisplaysDataType | grep \"Chipset Model\"' for GPU. "
        "Use 'df -H / | head -n 2' for disk space."
    )
    return shell_tool