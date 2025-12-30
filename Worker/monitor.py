
def collect_process_tree():
    """
    Minimal placeholder.
    In real version:
    - Parse Sysmon logs
    - Extract PID / PPID / Image
    """

    return {
        "root": "malware.exe",
        "children": [
            {
                "pid": 1234,
                "image": "cmd.exe",
                "children": [
                    {"pid": 5678, "image": "powershell.exe", "children": []}
                ]
            }
        ]
    }
