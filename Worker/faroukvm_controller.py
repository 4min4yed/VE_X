
import subprocess
from .faroukconfig import VM_NAME, VM_SNAPSHOT
from .faroukmonitor import collect_process_tree
from .faroukscreenshots import take_screenshot
from .farouksummarizer import generate_summary

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

def run_vm_analysis(job_id, file_path):
    print("🔁 Restoring VM snapshot")
    run_cmd(f'VBoxManage snapshot {VM_NAME} restore {VM_SNAPSHOT}')

    print("▶ Starting VM")
    run_cmd(f'VBoxManage startvm {VM_NAME} --type headless')

    print("🚀 Executing file in VM")
    run_cmd(
        f'VBoxManage guestcontrol {VM_NAME} run '
        f'--exe "C:\\sandbox\\{file_path}" '
        f'--username user --password pass'
    )

    print("📊 Collecting process tree")
    process_tree = collect_process_tree()

    print("📸 Taking screenshot")
    take_screenshot(job_id)

    print("🧠 Generating summary")
    summary = generate_summary(process_tree)

    print("⏹ Stopping VM")
    run_cmd(f'VBoxManage controlvm {VM_NAME} poweroff')

    print("RESULT:", summary)

