# Document Backup Tool

A small Python tool that backs up important document folders in two steps:

1. **Stage 1 (local):** new and changed files are copied to a backup folder on the computer.
2. **Stage 2 (ESD):** the local backup folder is copied to an external storage drive (ESD), for example a USB stick or an external disk.

```
Document folders --(Stage 1, automatic)--> C:\Backups\Datas --(Stage 2, manual)--> External drive
```

## 1. Why two stages

> The local copy (Stage 1) protects you from deleted or overwritten files. It is on the same physical disk as the originals, so it does **not** protect you if that disk fails.
> The external copy (Stage 2) is on a different device. It protects you if the computer disk fails. Keep the drive in a different place when you do not use it.

## 2. Main features

- **Incremental:** only new and changed files are copied. A second run with no changes copies nothing.
- **Never deletes:** a file you delete from the source stays in the backup. Cleaning the backup is a manual job.
- **Safety checks before copying to the drive:** a marker file must exist, the local backup folder must exist, and there must be enough free space.
- **Clear results:** every run writes log files, and the program ends with exit code `0` (success) or `1` (problem). Task Scheduler and the `.bat` file read this code.
- **One bad file does not stop the run:** a failed file is logged and the next file is copied.
- **No extra packages:** only the Python standard library is used.

## 3. Requirements

- Python 3.11 or newer (the code uses `tomllib`, which was added in 3.11).
- Windows for the `.bat` files and the Task Scheduler steps. The Python files are plain Python, but this guide and the batch files are written for Windows.

## 4. Project files

```
backup_tools.py       shared functions: config, logging, change detection, copying
backup_local.py       Stage 1: documents -> local backup folder
ESD_backup.py         Stage 2: local backup folder -> external drive
ESD_backup.bat        starts Stage 2 from the external drive (double-click)
setup_marker.bat      creates the marker file on the external drive (run once)
config.example.toml   template for your private config.toml
config.toml           your private settings (NOT in Git)
README.md             this file
.gitignore            tells Git what to ignore (must be named exactly ".gitignore")
```

## 5. Folders that are created while the tool runs

On the computer (the path comes from `BASE_PATH` in `config.toml`):

```
C:\Backups\
    Datas\
        study\          copy of the folder with name "study" in config.toml
        other\          copy of the folder with name "other"
    Logs\
        logs_for_backups.jsonl    normal events
        logs_for_errors.jsonl     problems
```

On the external drive:

```
E:\
    ESD_backup.bat
    setup_marker.bat
    Backups\
        marker_backup.txt         the marker file
        Datas\
            study\
            other\
```

The `.bat` files must stay in the root of the drive. The tool uses the folder of the `.bat` file as the drive location.

## 6. Setup, step by step

### Step 1: Get the code

Clone or download this project to a folder on your computer, for example `C:\Users\YourName\Projects\backup`. 

### Step 2: Create your `config.toml`

Copy `config.example.toml` to a new file named `config.toml` in the same folder as the Python files. Open it and change the paths:

```toml
BASE_PATH = 'C:/Backups'

[[source]]
name = 'study'
path = 'C:\Users\YourName\Documents\Study'

[[source]]
name = 'other'
path = 'C:\Users\YourName\Documents\Other'

[ESD]
safety_margin_gb = 1
```

Rules for this file:

- `BASE_PATH` must stay **above** the first `[header]`. Anything written below a header belongs to that header.
- Use **single quotes** for Windows paths. Single quotes keep the backslashes as they are. Double quotes would read `\U` as a special character and cause an error.
- Every `[[source]]` block adds one folder to back up. To add a folder, copy a block and change `name` and `path`.
- Each `name` must be unique. It becomes the folder name inside `Datas`.

### Step 3: Test Stage 1 by hand

Open Command Prompt or PowerShell in the project folder and run:

```
python backup_local.py
```

Check that `C:\Backups\Datas` now has a copy of your folders. Run it a second time. Nothing should be copied again. Open `C:\Backups\Logs\logs_for_backups.jsonl` to see the log.

### Step 4: Run Stage 1 automatically (Task Scheduler)

The goal is twice a month. In Windows, open **Task Scheduler** and choose **Create Task** (not Basic Task).

1. **General:** give the task a name, for example `Document Backup`.
2. **Triggers > New:** begin the task *On a schedule*, choose **Monthly**, select all months, and select days **1** and **15**. Pick a time, for example 12:00.
3. **Actions > New:** action *Start a program*.
   - Program/script: the full path of `python.exe`. Run `where python` in Command Prompt to find it. (`pythonw.exe` in the same folder runs without a black window.)
   - Add arguments: the full path of `backup_local.py` in quotes, for example `"C:\Users\YourName\Projects\backup\backup_local.py"`.
4. **Settings:** tick **Run task as soon as possible after a scheduled start is missed**. If the computer is off on day 1 or 15, the backup runs at the next start.
5. Click OK. Then right-click the task and choose **Run** to test it. Check the logs.

Task Scheduler shows the exit code in "Last Run Result". `0x0` means success. `0x1` means the tool reported a problem.

### Step 5: Prepare the external drive

1. Plug in the drive. Formatting is optional. If you format, use **exFAT** (works on Windows, macOS and Linux). Formatting erases everything on the drive.
2. Copy `ESD_backup.bat` and `setup_marker.bat` to the **root** of the drive.
3. Open `ESD_backup.bat` in a text editor and change the two lines at the top:
   - `SCRIPT` : the full path of `ESD_backup.py` on your computer.
   - `LOG_DIR` : the folder where logs are written (`BASE_PATH` + `\Logs`). It is only used for the message at the end.
4. Run `setup_marker.bat` **once**, from the drive. It shows where it will write and asks for confirmation. After you type `y`, it creates `Backups\marker_backup.txt` on the drive.

Why a marker file? It tells the program: "this is the backup drive, and a human chose it". If the `.bat` file is copied or run from another place, there is no marker, and the program stops. This protects you from writing a backup to the wrong disk.

### Step 6: Test Stage 2

1. Double-click `ESD_backup.bat` on the drive. You should see `Backup finished successfully.`
2. Check that `Backups\Datas` on the drive has your folders.
3. Test the failure path once: rename `marker_backup.txt`, run the `.bat` again, and check that it says `BACKUP FAILED - exit code 1`. Then rename the marker back.

## 7. Daily use

- **Stage 1** runs by itself on days 1 and 15. You can also run it by hand with `python backup_local.py`.
- **Stage 2:** plug in the drive and double-click `ESD_backup.bat`. Read the last message in the window, then press any key.
- Do Stage 2 after Stage 1 has run, because Stage 2 copies what Stage 1 has collected.

## 8. Configuration reference

| Setting | Where | Required | Meaning |
|---|---|---|---|
| `BASE_PATH` | top of file, before any header | yes | Backup folder on the computer. Use an absolute path. `~` is **not** expanded here. |
| `name` | in each `[[source]]` | yes | Name of the folder inside `Datas`. Must be unique. |
| `path` | in each `[[source]]` | yes | Folder to back up. Use single quotes. `~` is expanded here. |
| `safety_margin_gb` | in `[ESD]` | no (default 1) | Free space that must remain on the drive after copying, in GB. |

The copy to the drive stops if `space needed + safety margin` is bigger than the free space.

## 9. Logs

The tool writes two files in `BASE_PATH\Logs`:

- `logs_for_backups.jsonl` : normal events (start, finish, how many files were copied per folder).
- `logs_for_errors.jsonl` : problems (folder not found, file could not be copied, not enough space).

Both files use the **JSONL** format: one JSON object per line, new lines are always added at the end. A crash cannot damage old lines.

Example lines:

```json
{"run_id": "20261028T095240Z-61cf", "time": "2026-10-28T09:52:40", "location": "backup_local/main", "message": "folder done", "folder": "study", "copied": 3, "failed": 0}
{"run_id": "20261028T095240Z-61cf", "time": "2026-10-28T09:52:41", "location": "backup_tools/copy_files", "message": "copy failed", "error_type": "PermissionError", "error": "[Errno 13] Permission denied", "file": "C:\\Users\\YourName\\Documents\\Study\\report.docx"}
```

Fields:

- `run_id` : one id per program start, built from the UTC start time and 4 random characters. All lines of one run have the same id, so you can find everything that happened in one run. The time comes first, so sorting the ids sorts the runs by time.
- `time` : local time of this line.
- `location` : which part of the code wrote the line.
- `message` : short text. Other fields (`folder`, `copied`, `failed`, `file`, ...) give details.

Reading the logs with pandas:

```python
import pandas as pd

df = pd.read_json('C:/Backups/Logs/logs_for_backups.jsonl', lines=True)
print(df[df['message'] == 'folder done'].groupby('folder')['copied'].sum())
```

The log files only grow. There is no automatic cleanup yet.

## 10. How each file works

### `backup_tools.py` (shared functions)

It is imported by the other two scripts. It does not run by itself.

When it is imported, it reads `config.toml` once. If the file is missing, the program stops with a clear message.

Constants:

- `CONFIG` : the content of `config.toml` as a Python dictionary.
- `BASE_PATH_FOR_BACKUP` : the backup folder (`BASE_PATH`).
- `DATA_PATH` : `BASE_PATH_FOR_BACKUP / 'Datas'`, where the copies are stored.
- `LOGS_FOR_BACKUPS`, `LOGS_FOR_ERRORS` : the two log files.
- `TOLERANCE` : 2 seconds, used when comparing file times.
- `RUN_ID` : the id of this run.

Functions:

- `load_config()` : finds `config.toml` next to the script file (not in the current folder, so it works from any place) and reads it. The file is opened in binary mode because `tomllib` requires it.
- `write_jsonl(path, data)` : creates the log folder if needed, adds `run_id` and `time` to the data, and appends one JSON line to the file.
- `log_info(location, message, **fields)` : writes a normal event to `logs_for_backups.jsonl`.
- `log_error(location, message, error=None, **fields)` : writes a problem to `logs_for_errors.jsonl` and prints a short `ERROR` line on the screen. If an exception is given, its type and text are saved too.
- `change_check(source, target)` : walks through all files in `source` and returns a list of `(source_file, target_file)` pairs for the files that must be copied (see section 11). It does not copy anything.
- `copy_files(pairs)` : copies every pair with `shutil.copy2` (which also keeps the modification time). It creates missing folders. If one file fails, it logs the error and goes on. It returns the number of files that were copied.

### `backup_local.py` (Stage 1)

Flow:

1. Log "local backup started".
2. For each `[[source]]` in the config:
   - If the folder does not exist: log an error, count a problem, go to the next folder.
   - Otherwise: build the target path `Datas/<name>`, call `change_check`, call `copy_files`, and log one summary line with `copied` and `failed`.
   - If something unexpected crashes for one folder, log it and continue with the next folder. Folders do not stop each other.
3. Log "local backup finished".
4. If there was any problem, end with exit code 1. Otherwise exit code 0.

### `ESD_backup.py` (Stage 2)

It must be started from the drive location (the `.bat` file does this), because it uses the current folder as the drive location.

Flow, in this order (cheap checks first, copying last):

1. Log "ESD backup started".
2. Check that `Backups\marker_backup.txt` exists on the drive. If not, stop.
3. Check that the local `Datas` folder exists. If not, stop.
4. Call `change_check` to find the files that are new or changed.
5. Add up their sizes and read the free space of the drive.
6. If the size plus the safety margin is more than the free space, stop **before** copying anything. This avoids half-finished backups.
7. Copy the files with `copy_files`, then log how many were copied and how many failed.
8. If any file failed, report a problem and end with exit code 1.

The helper `fail(message, **fields)` writes the error to the log and ends the program with exit code 1.

### `ESD_backup.bat`

Runs on Windows from the drive:

1. Changes to its own folder (`cd /d "%~dp0"`). `%~dp0` means "the drive and folder of this file".
2. Checks that Python can be found. If not, it prints a clear message and stops.
3. Starts `ESD_backup.py` and saves its exit code.
4. Prints `Backup finished successfully.` for code 0, or `BACKUP FAILED` with the code and the log folder for any other code.
5. Waits for a key press (`pause`) so the window stays open.

### `setup_marker.bat`

Run it once, from the drive. It shows the folder where it will write, asks for `y` to confirm, creates the `Backups` folder if needed, and creates the empty `marker_backup.txt` file.

### `config.example.toml`

A template that is safe to put in Git. Copy it to `config.toml` and change the paths.

## 11. How a file is chosen for copying

`change_check` compares each source file with the file at the target path. A file is copied when:

1. it does not exist in the target, or
2. its size is different, or
3. the source file is newer than the target file by more than 2 seconds.

If the size is the same and the source is not newer, the file is skipped.

Two details:

- `shutil.copy2` keeps the modification time of the file. Without this, every copy would look "new" and the next run would copy everything again.
- The 2 second tolerance exists because some file systems (FAT, exFAT) round times. Without it, files would look changed on every run.

## 12. Safety rules and design decisions

- **No deleting.** The tool never removes files from a backup.
- **Marker file.** The marker is created **by hand, once**. A script that creates the marker on every run would make the check useless.
- **Check space first.** Free space is checked before the first file is copied.
- **Errors are caught at three levels:** per file (in `copy_files`), per folder (in `backup_local.py`), and at the end through the exit code.
- **Exit codes.** `0` means everything worked. `1` means at least one problem. Never ignore a `1`.
- **Config is read from the script folder,** not from the current folder, so the tool works from Task Scheduler and from the drive.

## 13. Troubleshooting

| Message or symptom | Meaning | What to do |
|---|---|---|
| `config.toml not found` | There is no `config.toml` next to the scripts | Copy `config.example.toml` to `config.toml` and edit it |
| `source folder not found` | A `path` in the config does not exist | Check the path in `config.toml`. Copy it from the Explorer address bar |
| `marker file not found` | Wrong location, or setup was not done | Run the `.bat` from the drive root. Run `setup_marker.bat` once |
| `local data folder not found` | Stage 1 has never run | Run `python backup_local.py` first |
| `not enough free space on the ESD` | The drive is too full | Free space, use a bigger drive, or lower `safety_margin_gb` |
| `copy failed` with `PermissionError` | A file is open in another program (for example Word) | Close the program and run again. The file is copied next time |
| `Python was not found` | Python is not installed or not in PATH | Install Python and tick "Add python.exe to PATH" |
| Exit code `9009` | Windows could not find the `python` command | Same as above. A Microsoft Store shortcut named `python` can also cause this |
| `TOMLDecodeError` | The config has a syntax error | Check single quotes around Windows paths and the position of `BASE_PATH` |
| Windows shows the task result `0x1` | The tool reported a problem | Read `logs_for_errors.jsonl` |

## 14. Restoring files

A backup is only useful if you can restore it. Your files are normal copies in normal folders:

- from the computer: `C:\Backups\Datas\<name>`
- from the drive: `Backups\Datas\<name>`

Copy them back with Explorer, or with `robocopy` in Command Prompt or PowerShell (not in Git Bash):

```
robocopy "E:\Backups\Datas\study" "C:\Users\YourName\Documents\Study" /E
```

Test a restore once into a temporary folder, so that you know it works before you need it.

## 15. Known limitations and ideas

- No cleanup: deleted files stay in the backup, and the drive slowly fills up.
- No ignore list yet (for example Office temporary files that start with `~$`, `*.tmp`, `Thumbs.db`). Open files cause `PermissionError` messages.
- No check after copying (for example comparing sizes or hashes).
- No dry-run mode (show what would be copied without copying).
- Do not put a live database file (for example SQLite) in a source folder. Copying a file that is in use can give a broken copy. Use a database-aware backup for databases.
- The backup is not encrypted. If the drive can be lost, consider BitLocker or VeraCrypt.
- No automatic tests yet.
- No protection against two runs at the same time.

## 16. Privacy and Git

- `config.toml` contains personal paths. It must be listed in `.gitignore`. The same is true for `Datas/` and `Logs/`.
- The ignore file must be named `.gitignore` (with the dot). A file named `_gitignore` is not used by Git.
- Before the first commit, run `git status` and check that `config.toml` is not in the list. A file that was committed once stays in the Git history even after you delete it.