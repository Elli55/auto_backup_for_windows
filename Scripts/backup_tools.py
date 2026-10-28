import shutil as sh
import datetime as dt
from datetime import timezone
from pathlib import Path 
import secrets
import json
import tomllib


CONFIG_FILE = Path(__file__).parent / 'config.toml'

def load_config():
    if not  CONFIG_FILE.exists():
        raise SystemExit('config.toml not found. Copy config.example.toml to or edit it.')
    
    with open(CONFIG_FILE, 'rb') as f:
        return tomllib.load(f)   
CONFIG = load_config()



BASE_PATH_FOR_BACKUP = Path(CONFIG['BASE_PATH'])
LOGS_FOR_BACKUPS = BASE_PATH_FOR_BACKUP / 'Logs' / 'logs_for_backups.jsonl'
LOGS_FOR_ERRORS = BASE_PATH_FOR_BACKUP / 'Logs' / 'logs_for_errors.jsonl' 
RUN_ID = f"{secrets.token_hex(2)}-{dt.datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"




def write_logs(e, file_name: str, message):

    TIMEING_FOR_LOGS = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    LOGS_FOR_ERRORS.parent.mkdir(parents=True, exist_ok=True)
    LOGS_FOR_BACKUPS.parent.mkdir(parents=True, exist_ok=True)

    if e == 0:

        data = {
                    'run_id': RUN_ID,
                    'date_time': TIMEING_FOR_LOGS,
                    'file_name': file_name,    
                    'message': str(message)
                }
        
        with open(LOGS_FOR_BACKUPS, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
         

    else:
        
        data = {
            'run_id': RUN_ID,
            'date_time': TIMEING_FOR_LOGS,
            'file_name': file_name,
            'type': type(e).__name__,
            'message': str(e)
        }

        with open(LOGS_FOR_ERRORS, 'a', encoding='utf-8') as f:
            json.dump(f, data, ensure_ascii=False, indent=4)

        return print(f'{message} for {file_name}')    


def change_check(source, target):


    changed = []

    try:

        for file in source.rglob('*'):

            if not file.is_file():
                continue

            new_file = target / file.relative_to(source)

            if new_file.exists():

                same_size = file.stat().st_size == new_file.stat().st_size
                not_newer = file.stat().st_mtime <= new_file.stat().st_mtime + 2

                if same_size and not_newer:
                    continue

            changed.append((file, new_file))

        return changed

    except Exception as e:
        write_logs(e, 'backup_tools/change_check', '')




def copy_files(paths):

    copied = 0

    try:

        for file, new_file in paths:

            try:
                new_file.parent.mkdir(parents=True, exits_ok=True)
                sh.copy2(file, new_file)
                copied += 1
                write_logs(0,str(file), f' After all change -{file}- copied to -{new_file}- . ')

            except Exception as e:
                write_logs(e, file, 0 )

        return copied        

    except Exception as e:
        write_logs(e, 'backup_tools/copy_files', '')
                







    

    



    