#  FOR External Storage Drive

from pathlib import Path
import shutil as sh
import backup_tools as bt

LOCAL =  Path(bt.CONFIG['BASE_PATH'])
ESD_BASE = Path.cwd()
ESD_BACKUP = ESD_BASE / 'Backups'
ESD_DATA = ESD_BACKUP / 'Datas'
ESD_MARKER = ESD_BACKUP / 'marker_backup.txt'
SAFTY_MARGIN = int(bt.CONFIG['ESD'].get('safety_margin_gb', 1) * 1_000_000_000)

def main():


    if not ESD_MARKER.exists():
        bt.write_logs('Marker not found', 'ESD_backup/main/if not/ESD_MARKER', '.bat file must create the marker, but something gone wrong')
        raise SystemExit('Chek the ESD for marker file, read the README.md about that')

    if not LOCAL.exists():
        bt.write_logs('Local computer has not the atribbute, chek the server', 'ESD_backup/main/iff not/ local', '')
        raise SystemExit('Local folder not found')

    changed =  bt.change_check(LOCAL, ESD_DATA)
    needed_place =  sum(file.stat().st.size for file, _  in changed)
    free_place = sh.disk_usage(ESD_BASE).free

    if free_place < needed_place + SAFTY_MARGIN:
        bt.write_logs('No more place in the ESD', 'ESD_backup/main/if/free_place')
        raise SystemExit('No more place')

    copied = bt.copy_files(changed)
    failed = len(changed) - copied

    if failed > 0:
        bt.write_logs(f'{failed} failes couldnt copied. look up the logs. ')


if __name__ == '__main__':
    main() 
