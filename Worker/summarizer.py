
def generate_summary(process_tree):
    reasons = []

    def walk(node):
        if "cmd.exe" in node["image"]:
            reasons.append("Spawned command interpreter")
        if "powershell.exe" in node["image"]:
            reasons.append("Spawned PowerShell")
        for c in node.get("children", []):
            walk(c)

    walk(process_tree)

    risk = "High" if reasons else "Low"

    return {
        "risk_level": risk,
        "reasons": list(set(reasons)),
        "message": (
            "This file shows suspicious behavior."
            if risk == "High"
            else "No suspicious behavior detected."
        )
    }
