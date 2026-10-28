from pathlib import Path


# path = Path(__file__).parent.parent / 'config.toml'

# print(path)



path = Path(__file__).parent.parent / 'Datas/study/OsnaUni/Anfang/045 Immabescheinigung.pdf'

print(path)

print(float(path.stat().st_size ), 'GB')