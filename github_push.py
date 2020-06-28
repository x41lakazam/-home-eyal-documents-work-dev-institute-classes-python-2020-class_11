from github import Github, GithubException
import smtplib
import email
import os
import pathlib

import getpass

def create_repo(repo_name):
    repo = user.create_repo(repo_name)
    return repo

def get_repo(repo_name):
    repo = user.get_repo(repo_name)
    return repo

def add_file(repo, path, commit_msg="", branch="master"):
    content = open(path, 'r').read()
    r = repo.create_file(path, commit_msg, content, branch=branch)
    print("[+] Added {} to {}".format(path, repo))

    return r

def update_file(repo, path, sha, commit_msg="", branch="master"):
    content = open(path, 'r').read()
    print("SHA:", sha)
    r = repo.update_file(path, commit_msg, content, sha, branch=branch)
    print("[*] Updated {}".format(path, repo))
    return r

def commit_files(repo, paths, commit_msg="", branch="master"):
    for path in paths:
        print("PATH:", path)
        try:
            # Check if file exists
            curr_content = repo.get_contents(path)
            r = update_file(repo, path, curr_content.sha, commit_msg, branch)
        except GithubException:
            try:
                r = add_file(repo, path, commit_msg, branch)
            except UnicodeDecodeError:
                continue

def get_dir_paths(cwd='.'): # '.' means current dir
    l = []
    for curr_dir, dirs, files in os.walk(cwd):
        for fname in files:
            path = os.path.join(curr_dir, fname)
            l.append(path.lstrip('./'))

    return l

def send_repo_by_mail(receiver_addr, pwd, msg, subject=""):
    send_mail(receiver_addr, pwd, msg, subject)

def send_mail(receiver_addr, pwd, msg, subject=""):
    receiver = 'eyal.work@chocron.eu'

    s = smtplib.SMTP("smtp.live.com",587)
    s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(sender,pwd)

    parts = ("From: " + mail_addr,
             "To: " + receiver,
             "Subject: " + subject,
             "",
             msg
             )
    msg ='\r\n'.join(parts)

    s.sendmail(mail_addr, receiver, msg)

    s.quit()

if __name__ == "__main__":
    user_name = "x41lakazam"
    repo_name = os.getcwd()
    mail_addr = 'yourmail@something.com'
    teacher_mail = "eyal.work@chocron.eu"

    pwd = getpass.getpass(prompt=f"Password for {user_name}: ")
    mail_pwd = getpass.getpass(prompt=f"Password for {mail_addr}: ")

    g = Github(user_name, pwd)
    user = g.get_user()

    try:
        repo = create_repo(repo_name)
    except:
        repo = get_repo(repo_name)

    paths = get_dir_paths()
    commit_files(repo, paths)

    # Send it by email
    repo_url = f"github.com/{user}/{repo_name}"

    print("Choose the type of content:")
    print("1) Homework")
    print("2) Daily Challenge")
    print("3) Awesome Project")
    choice = input("> ").strip()
    msg_by_choice = {
        "1": f"Here is my homework, check it at {repo_url}",
        "2": f"Here is my Daily Challenge, check it at {repo_url}",
        "3": f"Here is my Awesome project, check it at {repo_url}",
    }
    subject_by_choice = {
        "1": f"Homework",
        "2": f"Daily Challenge",
        "3": f"Awesome Project",
    }

    custom_msg = input("Additional message: ")

    message = msg_by_choice[choice]
    message += "\n" + custom_msg
    send_repo_by_mail(teacher_mail, mail_pwd, message, subject=subject_by_choice[choice])
