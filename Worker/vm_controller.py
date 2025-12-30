import subprocess
from .config import VM_NAME, VM_SNAPSHOT
from .monitor import collect_process_tree
from .screenshots import take_screenshot
from .summarizer import generate_summary

VBOX = r'"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"'

def run_cmd(cmd):
    full_cmd = f'{VBOX} {cmd}'
    subprocess.run(full_cmd, shell=True, check=True)

def run_vm_analysis(job_id, file_path):
    print("Restoring VM snapshot")
    run_cmd(f'snapshot "{VM_NAME}" restore "{VM_SNAPSHOT}"')

    print("Starting VM")
    run_cmd(f'startvm "{VM_NAME}" --type headless')

    print("Executing file in VM")
    run_cmd(
        f'guestcontrol "{VM_NAME}" run '
        f'--exe "C:\\sandbox\\{file_path}" '
        f'--username user --password pass'
    )

    print("Collecting process tree")
    process_tree = collect_process_tree()

    print("aking screenshot")
    take_screenshot(job_id)

    print("Generating summary")
    summary = generate_summary(process_tree)

    print("Stopping VM")
    run_cmd(f'controlvm "{VM_NAME}" poweroff')

    print("RESULT:", summary)
