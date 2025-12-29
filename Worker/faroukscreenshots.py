
import subprocess
from .faroukconfig import VM_NAME, RESULTS_PATH

def take_screenshot(job_id):
    path = f"{RESULTS_PATH}/{job_id}.png"
    subprocess.run(
        f'VBoxManage controlvm {VM_NAME} screenshotpng {path}',
        shell=True,
        check=True
    )
    return path

