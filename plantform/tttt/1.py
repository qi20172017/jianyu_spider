from fontTools.ttLib import TTFont

# 读取字体文件
font = TTFont('/Users/qifumin/Muto/plantform/tttt/szec.ttf')

# 获取字体文件中的所有字符
cmap = font.getBestCmap()
characters = [chr(c) for c in sorted(cmap.keys())]

# 输出所有字符
# print('所有字符:')
print(' '.join(characters))
print(cmap)
print(cmap.keys())

characters = [c for c in sorted(cmap.keys())]
print(characters)