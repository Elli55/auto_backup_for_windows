import shutil as sh
import datetime as dt
from datetime import timezone
from pathlib import Path 
import secrets
import json


BASE_PATH_FOR_BACKUP = Path('C:/Backups')
LOGS_FOR_BACKUPS = BASE_PATH_FOR_BACKUP / 'Logs' / 'logs_for_backups.txt'
LOGS_FOR_ERRORS = BASE_PATH_FOR_BACKUP / 'Logs' / 'logs_for_errors.jsonl' 
TIMEING_FOR_LOGS = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
RUN_ID = f'{secrets.token_hex(2)}-{dt.datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}'




def write_logs(e, file_name: str, message):

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
                json.dump(f, data, ensure_ascii=False, indent=4)
         

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

                same_size = file.state().st_size() == new_file.state().st_size()
                not_newer = file.state().st_mtime() <= new_file.state().st_mtime() + 2

                if same_size and not_newer:
                    continue

            changed.append((source, target))

            return changed

    except Exception as e:
        write_logs(e, 'backup_tools/change_check', '')

        


def copy_files(paths):

    copied = 0

    try:

        for file, new_file in paths:

            try:
                new_file.parent.mkdir(parents=True, exists_ok=True)
                sh.copy2(file, new_file)
                copied += 1
                write_logs(0,file, f' After all change -{file}- copied to -{new_file}- . ')

            except Exception as e:
                write_logs(e, file, 0 )

    except Exception as e:
        write_logs(e, 'backup_tools/copy_files', '')
                







    

    



    