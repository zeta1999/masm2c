del iplay_nasm.obj iplay_nasm.exe
nasm.exe -f obj -Ox iplay_nasm.asm -l iplay_nasm.lst 
rem wlink  name iplay_nasm.exe system dos file iplay_nasm.obj option verbose
alink -m -oEXE iplay_nasm.obj
D:\upx.exe  --ultra-brute iplay_nasm.exe
type IPLAY.PCT >> iplay_nasm.exe