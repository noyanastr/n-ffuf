#!/usr/bin/env python3

import subprocess #python üzerinde terminal komutu çalıştırmak için
import re #regex için kullanılıyor burada ise dosya adını temizlemek için kullanılıyor
from datetime import datetime #rapor içine tarih damgası eklemek için kullanıyoruz
from pathlib import Path #klasör ve dosya yolu işlemleri için


CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def run_command(command): #command adında bir terminal komutu alır
    try: #hata çıkabilecek kodları güvenli çalıştırmak için
        result = subprocess.run(#terminal komutu çalıştırır
            command,#çalıştırılacak komut budur
            shell=True,#komutu shell üzerinden çalıştırır
            text=True,#çıktıyı yazı olarak alır yoksa çıktı bytes olarak gelebilir
            stdout=subprocess.PIPE,#terminal çıktısını yakalar
            stderr=subprocess.STDOUT#hata çıktısını da normal çıktıya ekler yani hata da rapora yazılır
        )
        return result.stdout#komutun çıktısını geri döndürür
    except Exception as e:
        return f"Komut çalıştırılırken hata oluştu: {e}"


def clean_filename(target):
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", target)#farklı karakterleri _ olarak yazar böylece raporda ya da çıktıda sorun yaşanmaz


def banner():

    print(f"""{CYAN}
███╗   ██╗      ███████╗███████╗██╗   ██╗███████╗
████╗  ██║      ██╔════╝██╔════╝██║   ██║██╔════╝
██╔██╗ ██║█████╗█████╗  █████╗  ██║   ██║█████╗  
██║╚██╗██║╚════╝██╔══╝  ██╔══╝  ██║   ██║██╔══╝  
██║ ╚████║      ██║     ██║     ╚██████╔╝██║     
╚═╝  ╚═══╝      ╚═╝     ╚═╝      ╚═════╝ ╚═╝     

        FFUF Automation Tool
          
{RESET}""")
def show_menu(): #burası kullanıcıya seçenek gösterir ve her döngüde bunu yazdırır
    print(f"""{GREEN}
========================================
             N-FFUF TOOL
========================================

[1] Start Directory Fuzzing
[2] Help
[0] Exit
{RESET}
""")

def select_wordlist():#kullanıcıya burada wordlist seçtirir
    print(f"""{GREEN}
Select a wordlist:

[1] dirb common.txt
[2] SecLists common.txt
[3] I will enter the path manually
{RESET}
""")

    choice = input(f"{YELLOW}Selection: {RESET}").strip()

    if choice == "1":
        return "/usr/share/wordlists/dirb/common.txt"

    elif choice == "2":
        return "/usr/share/seclists/Discovery/Web-Content/common.txt"

    elif choice == "3":
        return input(f"{YELLOW}Enter the wordlist path: {RESET}").strip()

    else:
        print(f"{RED}[-] Invalid selection. The default wordlist will be used.{RESET}")
        return "/usr/share/wordlists/dirb/common.txt"


def prepare_target(target):#FFUF çalışması için http:// ya da https://'e ihtiyaç duyar bunun için vardır
    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    if "FUZZ" not in target:
        if target.endswith("/"):
            target = target + "FUZZ"
        else:
            target = target + "/FUZZ"

    return target


def ffuf_scan(target, wordlist):#asıl taramanın olduğu yer

    command = f"ffuf -u {target} -w {wordlist} -mc 200,301,302,403"#200=sayfaVar, 301=kalıcıYönlendirme, 302=geçiciYönlendirme, 403=yasaklıFakatŞüpheli

    output = run_command(command)

    results = []

    for line in output.splitlines():

        if "[Status:" in line:

            cleaned_line = line.strip()

            if cleaned_line not in results:
                results.append(cleaned_line)

    if not results:
        return "No results found."

    return "\n".join(results)


def generate_report(target, wordlist, ffuf_result):#burası rapor oluşturma kısmıdır
    reports_dir = Path("reports")#reports klasörünü temsil eder
    reports_dir.mkdir(exist_ok=True)#eğer klasör yoksa oluşturur varsa hata vermez es geçer

    filename = reports_dir / f"{clean_filename(target)}_ffuf_report.txt"
#geri kalan kısım rapor metnini hazırlar
    report = f""" 
======================================== 
              N-FFUF REPORT
========================================

Target      : {target}
Wordlist    : {wordlist}
Scan Date   : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

========================================
              FFUF RESULT
========================================

{ffuf_result}

========================================
              END OF REPORT
========================================
"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(report)

    return filename


def start_scan():
    target = input(f"{YELLOW}[?] Enter the target URL/domain: {RESET}").strip()

    if not target:
        print(f"{RED}[-] The target cannot be left blank.{RESET}")
        return

    wordlist = select_wordlist()
    target = prepare_target(target)

    print(f"{GREEN}[+] Target prepared: {target}{RESET}")
    print(f"{GREEN}[+] Wordlist: {wordlist}{RESET}")
    print(f"{GREEN}[+] Starting the FFUF scan...{RESET}")

    ffuf_result = ffuf_scan(target, wordlist)

    print(f"{GREEN}[+] Generating the report...{RESET}")
    report_file = generate_report(target, wordlist, ffuf_result)

    print(f"{GREEN}[+] Report generated: {report_file}{RESET}")


def show_help():
    print(f"""{GREEN}
========================================
                HELP
========================================

This tool should only be used on authorized targets.

How it works:

1.The user enters the target URL/domain
2.A wordlist is selected
3.FUZZ is added into the URL
4.Directory fuzzing is performed with FFUF
5.The results are saved as a TXT report

Example targets:
example.com
http://example.com
https://example.com
https://example.com/FUZZ
{RESET}
""")


def main():
    banner()

    while True:
        show_menu()
        choice = input(f"{YELLOW}Selection: {RESET}").strip()

        if choice == "1":
            start_scan()

        elif choice == "2":
            show_help()

        elif choice == "0":
            print(f"{GREEN}[+] Exiting...{RESET}")
            break

        else:
            print(f"{RED}[-] Invalid selection!{RESET}")


if __name__ == "__main__":
    main()
