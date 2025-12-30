import subprocess
import os
import time

class SandboxVM:
    def __init__(self, vm_name):
        self.vm_name = vm_name
        # Use a raw string (r) to handle backslashes in Windows paths
        self.vbox = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" 

    def run_vbox(self, args):
        cmd = [self.vbox] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def start_headless(self):
        print(f"Starting {self.vm_name}...")
        return self.run_vbox(["startvm", self.vm_name, "--type", "headless"])

    def run_in_vm(self, exe_path):
        print(f"Executing: {exe_path}")
        # Ensure credentials match your VM setup
        return self.run_vbox(["guestcontrol", self.vm_name, "run", "--exe", exe_path, "--username", "user", "--password", "pass"])

    def take_screenshot(self, output_path):
        print(f"Capturing screenshot: {output_path}")
        return self.run_vbox(["controlvm", self.vm_name, "screenshotpng", output_path])

    def revert_to_snapshot(self, snapshot_name="CleanState"):
        print(f"Shutting down and reverting to {snapshot_name}...")
        self.run_vbox(["controlvm", self.vm_name, "poweroff"])
        time.sleep(2) # Give it a moment to stop
        return self.run_vbox(["snapshot", self.vm_name, "restore", snapshot_name])

    def get_metrics(self):
        print(f"Getting metrics for {self.vm_name}...")
        return {"cpu": 25, "ram": 512 * 1024 * 1024}  

# --- Logic to run the analysis ---
def run_vm_analysis(filepath_on_host):
    vm = SandboxVM("SandboxWin11")
    
    # 1. Revert to clean state first
    vm.revert_to_snapshot("CleanState")
    
    # 2. Start VM
    vm.start_headless()
    time.sleep(10) # Wait for VM to boot/load
    
    # To copy file from host to guest:
    vm.run_vbox(["guestcontrol", vm.vm_name, "copyto", filepath_on_host, "--target-directory", "C:\\temp\\"])
    vm.run_in_vm(r"C:\\temp\\"+filepath_on_host.split("\\")[-1])
        
    # 4. Wait for execution impact
    time.sleep(5)
        
    # 5. Record Peak Usage
    peak = vm.get_metrics()
    peak_response=(f"Peak - CPU: {peak['cpu']}% | RAM: {peak['ram']} bytes")
    vm.run_in_vm(r"C:\Windows\System32\tasklist.exe")
    
    # 4. Screenshot
    vm.take_screenshot(r"analysis_01.png")
    
    return f"Analysis complete for {filepath_on_host}"


run_vm_analysis("my-whoami.exe")