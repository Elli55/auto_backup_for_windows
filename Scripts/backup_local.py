import backup_tools as bt
from pathlib import Path

def main():

    try:

        for i in bt.CONFIG['source']:

            name = i['name']
            path = Path(i['path'])

            if not path.exists():
                bt.write_logs('Path error', f'{name}', f'check this path -{path}- .')
                continue

            target = Path(bt.BASE_PATH_FOR_BACKUP / 'Datas' / name)
            changed = bt.change_check(path, target)
            copied = bt.copy_files(changed)
            bt.write_logs(0, f'{name}', f'for {name}: {copied} files copied')

    except Exception as e:
        bt.write_logs(e, 'backup_locak/main', '')


main()
