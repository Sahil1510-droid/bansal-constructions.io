import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import webbrowser


# ---------- GIT COMMAND RUNNER ----------
def run_command(command, cwd):
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise Exception(error)
    return result.stdout


# ---------- FILE / FOLDER SELECT ----------
def select_folder():
    path = filedialog.askdirectory()
    if path:
        selected_path.set(path)
        selected_files.clear()
        mode.set("folder")


def select_files():
    files = filedialog.askopenfilenames()
    if files:
        selected_files.clear()
        selected_files.extend(files)
        selected_path.set(f"{len(files)} files selected")
        mode.set("files")


# ---------- OPEN REPO URL ----------
def open_repo_url():
    url = repo_url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a GitHub repository URL")
        return
    webbrowser.open(url)


# ---------- MAIN PUSH LOGIC ----------
def push_to_github():
    repo_url = repo_url_entry.get().strip()
    commit_msg = commit_message_entry.get().strip()

    if not repo_url or not commit_msg:
        messagebox.showerror("Error", "Repository URL and commit message are required")
        return

    try:
        # Decide working directory & add command
        if mode.get() == "folder":
            cwd = selected_path.get()
            if not cwd or not os.path.isdir(cwd):
                raise Exception("No folder selected")
            add_command = "git add -A"

        elif mode.get() == "files":
            if not selected_files:
                raise Exception("No files selected")
            cwd = os.path.dirname(selected_files[0])
            files = " ".join([f'"{f}"' for f in selected_files])
            add_command = f"git add {files}"

        else:
            raise Exception("Please select a folder or files")

        # Init repo if missing
        if not os.path.exists(os.path.join(cwd, ".git")):
            run_command("git init", cwd)

        # Set remote safely
        run_command(f"git remote set-url origin {repo_url}", cwd)

        # Ensure main branch
        run_command("git checkout -B main", cwd)

        # Pull first (fixes non-fast-forward issues)
        try:
            run_command("git pull origin main --rebase", cwd)
        except Exception:
            pass

        # Add changes
        run_command(add_command, cwd)

        # Commit
        run_command(f'git commit -m "{commit_msg}"', cwd)

        # Push
        run_command("git push origin main", cwd)

        messagebox.showinfo("Success", "Upload completed successfully 🚀")

    except Exception as e:
        messagebox.showerror("Git Error", str(e))


# ---------- GUI ----------
root = tk.Tk()
root.title("GitHub Upload Tool")
root.geometry("650x430")
root.resizable(False, False)

mode = tk.StringVar()
selected_path = tk.StringVar()
selected_files = []

tk.Label(root, text="Upload Type", font=("Arial", 11, "bold")).pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Select Folder", width=22, command=select_folder).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Select Multiple Files", width=22, command=select_files).grid(row=0, column=1, padx=10)

tk.Entry(root, textvariable=selected_path, width=85, state="readonly").pack(pady=10)

tk.Label(root, text="GitHub Repository URL").pack()
repo_url_entry = tk.Entry(root, width=85)
repo_url_entry.pack(pady=5)

tk.Button(
    root,
    text="Open Repository URL",
    command=open_repo_url
).pack(pady=5)

tk.Label(root, text="Commit Message").pack()
commit_message_entry = tk.Entry(root, width=85)
commit_message_entry.pack(pady=5)

tk.Button(
    root,
    text="Upload to GitHub",
    bg="#24292e",
    fg="white",
    padx=22,
    pady=10,
    command=push_to_github
).pack(pady=25)

root.mainloop()