#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# env
import dotenv
dotenv.load_dotenv()

# imports
import os
# from langchain import (


# )
import langchain





# install dependencies
if not os.path.exists('requirements.txt'):
    print("[!] 'requirements.txt' NOT FOUND")
    print("[+] manually install the dependencies")

print("[+] Installing all the dependencies")
os.system("pip install -r requirements.txt")
print("\n[+] Installed")

# running code
print("[+] run 'python main.py' or 'python3 main.py'")
try:
    os.system('python main.py')
except:
    os.system('python3 main.py')
else:
    print("[!] python/python3 not found")
