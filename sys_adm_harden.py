#! /usr/bin/python3.6

# Tired of being hacked, not many tools out there for nix systems
# to help aid in hardening of the system(s)
# so, here is one that is helpful I like to think, and should be used.
# usage is simple, Specify if you are using bsd or debian based systems.
# @todo will keep a database of all files changed.
# sqlite3 would not install properly. 

try:
    import sys
    import os
    from time import sleep
    from tqdm import tqdm
    import sqlite3
    import queue
except ImportError as e:
    import sys
    print("One or more of the required packages did not import\n please run pip install -r requirements.txt "
          "before moving on.")
    sys.exit(1)
#############################################################################################################################    
#@todo, because I LOVE encryption, Need to impliment a way to encrypt this DB, because, science.
#I do not like to assume much, however, the os.path module will list the full path.
conn = sql3.connect('immutable.sqlite')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS SystemHardener(FileID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, FileName TEXT)""")
###############################################################################################################################

###############################################################################################################################
def walk(directory, chattr):
    #@todo, make this recursive and check all directories.
    #@todo, need to refine the logic here, it works, but still kind of buggy.
    li = list()
    result = set()
    flags = ''
    directories = list()
    reject = set()
    if chattr == "chflags": flags = "chflags schg sappend"
    if chattr == "chattr": flags = "chattr +i"
    for entry in os.listdir(directory):
        if entry == 'wpa_supplicant.conf':
            reject.add(entry)
            continue
        if entry.endswith('.conf'):
            li.append(entry)
    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=False):
            directories.append(entry)
            for entry in directories:
                links = os.scandir(entry)
                directories.remove(entry)
                for item in links:
                    if item.endswith('.conf'):
                        li.append(item)
    for entry in li:
        result.add(entry)
        for entry in result:
            stuff = flags + entry
            os.system(stuff)
            li.remove(entry)
    return "[!] Complete, moving on.... [!]"
##############################################################################################################################

conti = 'y'
while conti == 'y':
    try:
        # detmine which flavor the user is using.
        choice = str(input("[~] Are you using debian or BSD? [~]\n->")).lower()
        if choice == "debian":
            os.system('clear')
            print("[!] Selected %s [!]"% str(choice))
            chattr = 'chattr'
            cont = 'y'
            while cont == 'y':
                print('[!] Please note, the default is root(/) and it will scan all directories it finds. [!]')
                dire = str(input("[! Which directory would you like to scan? [!] \n->"))
                if dire == '':
                    dire = '/'
                walk(dire, chattr)
                print("[!] It is strongly suggested that you use chmod 600 on all files you want hidden that are not system"
                  "files, I STRONGLY ADVISE DOING THIS. SO YOUR PERSONAL DIRECTORY ETC.")
                break
            break
        if choice == "bsd":
            os.system('clear')
            print("[!] Selected %s [!]"% str(choice))
            # refer to the bsd manual for chflags to understand what is happening here.
            chattr = "chflags"
            stuff = {"kern_securelevel_enable=\"YES\"","\n","kern_securelevel=\"1\"","\n","pf_enable=\"YES\"","\n",
                     "pf_rules=\"/etc/pf.conf\"","\n","pflog_enable=\"YES\"","\n","pflog_file=\"/var/log/pf.log\"",
                     "accounting_enable=\"YES\""}
            print("[!] Will be using %s \n to secure files. [!]"% str(chattr))
            print("[!] Appending kern_securelevel_enable=YES and kern_securelevel=1 to rc.conf [!]")
            # @todo figure out why the eff this is happening, makes 0 sense. trying writelines instead of write.
            try:
                rc = open('/etc/rc.conf', 'a')
                rc.writelines(''.join(stuff))
                rc.close()
            except:
                pass
            print("[!] Finished, moving onto other config files [!]")
            cont = "y"
            while cont == "y":
                print('[!] Please note, the default is root(/) and it will scan all directories it finds. [!]')
                dire = str(input("[! Which directory would you like to scan? [!] \n->"))
                if dire == '':
                    dire = '/'
                walk(dire, chattr)
            continue
        if choice == '':
            print("[!!] Sorry, choice was empty, if you would like to exit,"\
                    " press CTRL+C [!!]")
            continue
    except KeyboardInterrupt as e:
        print("\n[+] CTRL C was pressed [+]\n")
        conti = str(input("[??] Did you make a mistake and would like to "\
            "restart? [??]\n->(y/N)")).lower()
        if conti == 'n':
            print("[!] Ok I love you bye-bye [!]")
            sys.exit(0)
        continue
