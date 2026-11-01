# 演示用：命令注入
import subprocess
from flask import request

def ping():
    host = request.args.get("host", "127.0.0.1")
    return subprocess.run("ping -c 1 " + host, shell=True, capture_output=True).stdout
