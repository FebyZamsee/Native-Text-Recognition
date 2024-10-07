""" NATIVE TEXT RECOGNITION """

import os,subprocess,uuid

class Err(Exception):
    ...
    
class NTR:
    def __init__(self) -> None:
        self.user = str(os.getenv("USERNAME"))
        self.memuPath = f"C:\\Users\\{self.user}\\Downloads\\MEmu Download"
        self.devicePath = f"/sdcard/Download"

    def adb(self,device: str, command: str, whereami=None, sudo=False):
        if "\n" in command:
            command = "; ".join([str(x).replace("\t", "").replace(
                "  ", "").strip() for x in command.strip().splitlines()])

        cmd = f'adb -s {device} shell echo; {command}'
        if sudo:
            cmd = f'adb -s {device} shell su -c "{command}"'
        print(cmd, f"| {whereami}")
        result = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            return output
        else:
            return result.stderr.strip()


    def boundToXY(self, data: str = '<node index="1" text="Continue as Vincenja" resource-id="u_0_0_6l" class="android.widget.Button" package="com.android.chrome" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[12,252][629,282]" />'
                  ) -> tuple:
        """ Ubah Bound data ke kordinat x,y untuk digunakan ke adb """
        data = data.split('bounds="')[1].split('"')[0]
        data = data[1:-1].split("][")
        data = [x.split(",") for x in data]
        x = round(int(int(data[0][0]) + int(data[1][0]))/2)
        y = round(int(int(data[0][1]) + int(data[1][1]))/2)
        return x,y

    def filterDataScreenToText(self,file: str="window_dump.xml", filterStr: str='Continue as'
                               ) -> list:
        """ Filter Data hasil screenshot berdasarkan text kata kunci """
        if not os.path.exists(file):
            raise Err("File gak ada!")
        with open(file, "r+", encoding="utf-8") as ff:
            data = ff.read().strip().replace("><", ">\n<")
            lines = data.splitlines()
        filtered = [x for x in lines if filterStr in x]
        return filtered

    def screenshotText(self, adb_device: str) -> str:
        device = adb_device
        uid = "."+str(uuid.uuid4()).replace("-","")[20:]+".xml"
        devicePath = f"{self.devicePath}/{uid}"
        save = self.adb(device, f"uiautomator dump --file {devicePath}")
        if save == f"UI hierchary dumped to: {devicePath}":
            savedPath = os.path.join(self.memuPath,uid)
            print(f"Saved in {savedPath}")
            return savedPath
        raise Err(f"NTR_FAIL_SS: {save}")

def test():
    device = "127.0.0.1:21633"  # contoh port adb memu || adb devices
    p = NTR()
    path = p.screenshotText(device)
    flterText = "Continue as"
    filter = p.filterDataScreenToText(path)
    print(filter)
    x,y = p.boundToXY(filter[0])
    print(x,y)
    p.adb(device,f"input tap {x} {y}")

