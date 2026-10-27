import backup_tools as bt
from pathlib import Path

def main():
    for i in bt.CONFIG['source']:

        name = i['name']
        path = Path(i['path'])

        if not path.exists():
            bt.write_logs()



