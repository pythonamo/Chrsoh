import threading
import socket
import time
import sys
from queue import Queue

stats = {
    "goods": 0,
    "not_ssh": 0,
    "timeout": 0,
    "refuse": 0,
    "error": 0
}

lock = threading.Lock()
status = True
q = Queue()

# ??????????????? ?? ????? ?????? ???
linux_distros = ['ubuntu', 'centos', 'debian', 'fedora', 'redhat', 'arch', 'suse']

def print_banner():
    while status or not q.empty():
        with lock:
            print(f"\033c", end="")  # Clear screen (optional)
            print("\033[1;36m-------------------------------------------\033[0m")
            print("\033[1;32m   SSH Scan Progress\033[0m")
            print("\033[1;36m-------------------------------------------\033[0m")
            print(f"\033[1;33mGoods (Linux Servers):\033[0m \033[1;32m{stats['goods']}\033[0m")
            print(f"\033[1;33mNot SSH Servers:\033[0m \033[1;31m{stats['not_ssh']}\033[0m")
            print(f"\033[1;33mTimeouts:\033[0m \033[1;33m{stats['timeout']}\033[0m")
            print(f"\033[1;33mRefused Connections:\033[0m \033[1;35m{stats['refuse']}\033[0m")
            print(f"\033[1;33mErrors:\033[0m \033[1;37m{stats['error']}\033[0m")
            print("\033[1;36m-------------------------------------------\033[0m")
            sys.stdout.flush()
        time.sleep(1)

def check_ssh(HOST, PORT, timeout_=2):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout_)
        try:
            s.connect((HOST, PORT))
            data = s.recv(1024).decode(errors='ignore')
            # ????? ???? ?????????????? ?????
            if any(distro in data.lower() for distro in linux_distros):  
                with lock:
                    stats["goods"] += 1
                return True, data.strip()  # ?????????? ?????? ??????? ???
            else:
                with lock:
                    stats["not_ssh"] += 1
                return False, data.strip()  # ???? ?? SSH ????? ????
        except socket.timeout:
            with lock:
                stats["timeout"] += 1
            return False, None
        except ConnectionRefusedError:
            with lock:
                stats["refuse"] += 1
            return False, None
        except Exception:
            with lock:
                stats["error"] += 1
            return False, None

def worker():
    while not q.empty():
        item = q.get()
        if ':' in item:
            ip, port = item.strip().split(':')
            try:
                port = int(port)
                ok, banner_data = check_ssh(ip, port)
                if ok:
                    # ??? ???? ?????? ???? ?? ?? ?? ???? ????? ??
                    with open("linux_servers.txt", "a") as f:
                        f.write(f"{ip}:{port}\n")
                if banner_data:
                    # ????? ???? ??????? ???
                    with open("out-iplist-out-vn.txt", "a") as f_banner:
                        f_banner.write(f"{ip}:{port}  --> {banner_data}\n")
            except ValueError:
                pass
        q.task_done()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 script.py ip_list.txt 100")
        sys.exit(1)

    list_ips = open(sys.argv[1]).read().splitlines()
    thread_count = int(sys.argv[2])

    for ip_port in list_ips:
        q.put(ip_port)

    threading.Thread(target=print_banner, daemon=True).start()

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    q.join()
    status = False

    for t in threads:
        t.join()
