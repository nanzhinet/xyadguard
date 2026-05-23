import os
import subprocess
import glob
import re
from pathlib import Path

os.chdir('tmp')

print("合并上游拦截规则")
file_list = glob.glob('adblock*.txt')
with open('combined_adblock.txt', 'w') as outfile:
    for file in file_list:
        with open(file, 'r') as infile:
            outfile.write(infile.read())
            outfile.write('\n')
            
with open('combined_adblock.txt', 'r') as f:
    content = f.read()
content = re.sub(r'^[!].*$\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#(?!\s*#).*\n?', '', content, flags=re.MULTILINE)

with open('cleaned_adblock.txt', 'w') as f:
    f.write(content)
print("拦截规则合并完成")

print("合并上游白名单规则")
allow_file_list = glob.glob('allow*.txt')
with open('combined_allow.txt', 'w') as outfile:
    for file in allow_file_list:
        with open(file, 'r') as infile:
            outfile.write(infile.read())
            outfile.write('\n')

with open('combined_allow.txt', 'r') as f:
    content = f.read()
content = re.sub(r'^[!].*$\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#(?!\s*#).*\n?', '', content, flags=re.MULTILINE)

with open('cleaned_allow.txt', 'w') as f:
    f.write(content)
print("白名单规则合并完成")

print("过滤白名单规则")
with open('cleaned_allow.txt', 'r') as f:
    allow_lines = f.readlines()

with open('combined_adblock.txt', 'a') as outfile:
    outfile.writelines(allow_lines)

with open('combined_adblock.txt', 'r') as f:
    lines = f.readlines()
with open('allow.txt', 'w') as f:
    for line in lines:
        if line.startswith('@'):
            f.write(line)
            
print("应用 mod/whitelist.txt 过滤误拦截域名")
mod_whitelist_path = '.././data/mod/whitelist.txt'
whitelist_domains = set()
with open(mod_whitelist_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        line = line.strip()
        # 提取 @@||domain^ 中的域名
        if line.startswith('@@||') and line.endswith('^'):
            domain = line[4:-1]
            if domain:
                whitelist_domains.add(domain)

print(f"mod 白名单共 {len(whitelist_domains)} 个域名，开始过滤拦截规则")

with open('cleaned_adblock.txt', 'r', encoding='utf-8', errors='ignore') as f:
    adblock_lines = f.readlines()

filtered_lines = []
removed_count = 0
for line in adblock_lines:
    stripped = line.strip()
    # 提取拦截规则中的域名（||domain^ 格式）
    if stripped.startswith('||') and stripped.endswith('^'):
        domain = stripped[2:-1]
        if domain in whitelist_domains:
            removed_count += 1
            continue  # 在白名单里，跳过不写入
    filtered_lines.append(line)

with open('cleaned_adblock.txt', 'w', encoding='utf-8') as f:
    f.writelines(filtered_lines)

print(f"过滤完成，共移除 {removed_count} 条误拦截规则")

current_dir = os.getcwd()
adblock_file = os.path.join(current_dir, 'cleaned_adblock.txt')
allow_file = os.path.join(current_dir, 'allow.txt')
target_dir = os.path.join(current_dir, '.././data/rules/')
Path(target_dir).mkdir(parents=True, exist_ok=True)
adblock_file_new = os.path.join(target_dir, 'adblock.txt')
allow_file_new = os.path.join(target_dir, 'allow.txt')
os.rename(adblock_file, adblock_file_new) 
os.rename(allow_file, allow_file_new) 

print("规则去重中")
os.chdir(".././data/rules/")  # 更改当前目录
files = os.listdir()  # 得到文件夹下的所有文件名称
result = []
for file in files:  # 遍历文件夹
    if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
        if os.path.splitext(file)[1] == '.txt':
            # print('开始去重'+(file))
            f = open(file, encoding="utf8")  # 打开文件
            result = list(set(f.readlines()))
            result.sort()
            fo = open('test' + (file), "w", encoding="utf8")
            fo.writelines(result)
            f.close()
            fo.close()
            os.remove(file)
            os.rename('test' + (file), (file))
            # print((file) + '去重完成')
print("规则去重完成")
