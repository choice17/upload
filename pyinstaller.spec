# -*- mode: python -*-
import sys
sys.setrecursionlimit(10000)
block_cipher = None


a = Analysis(['Multiplayer.py'],
             pathex=['C:\\Users\\im147\\Desktop\\workspace\\task\\4259 virtual lines\\multiplayer'],
             binaries=[('ffmpeg.exe','.'),('ffprobe.exe','.')],
             datas=[('opencv_ffmpeg341_64.dll', '.'), ('README.md', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4', 'PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

Key = ['mkl','libopenblas']

def remove_from_list(input, keys):
    outlist = []
    for item in input:
        name, _, _ = item
        flag = 0
        for key_word in keys:
            if name.find(key_word) > -1:
                flag = 1
        if flag == 1:
            print(name,'skip!!!!!!!!!!!!!!!!!!!!!!!')
        else:
            print(name,'append!!!!!!!!!!!!!!!!!!!!!!!')
            outlist.append(item)

    return outlist

a.binaries = remove_from_list(a.binaries, Key)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Multiplayer',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
