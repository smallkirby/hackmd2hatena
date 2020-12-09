keywords
libcbase, pwn, kanpan, heap feng shui, test

# イントロ
いつぞや開催された**HOGE CTF**。その**pwn**問題である**Can you here me?**を解いていく。
この問題は、***テスト***であり当然このエントリ自体もテストである。


# 静的解析
## 問題概要
```static.sh
$ file ./test
./test: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=2bc4d25d187796b44a43cf1001c8a6422eae2bd9, for GNU/Linux 3.2.0, not stripped
$ checksec --file ./test
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

## 見つけた脆弱性
今回見つけた脆弱性は以下の2つ。
1. わーい
2. うえーい


# exploitの方針
以下のコードで、*libcbase*がleakできる。
```test.c
int main(void){
  printf("hello");
  return 0;
}
```


# exploit
なお、本番環境では試していない。
```exploit.py
#!/usr/bin/env python
#encoding: utf-8;

from pwn import *
import sys

FILENAME = ""
LIBCNAME = ""

hosts = ("","localhost","localhost")
ports = (0,12300,23947)
rhp1 = {'host':hosts[0],'port':ports[0]}    #for actual server
rhp2 = {'host':hosts[1],'port':ports[1]}    #for localhost 
rhp3 = {'host':hosts[2],'port':ports[2]}    #for localhost running on docker
context(os='linux',arch='amd64')
binf = ELF(FILENAME)
libc = ELF(LIBCNAME) if LIBCNAME!="" else None


## utilities #########################################

def hoge():
  global c
  pass

## exploit ###########################################

def exploit():
  global c


## main ##############################################

if __name__ == "__main__":
    global c
    
    if len(sys.argv)>1:
      if sys.argv[1][0]=="d":
        cmd = """
          set follow-fork-mode parent
        """
        c = gdb.debug(FILENAME,cmd)
      elif sys.argv[1][0]=="r":
        c = remote(rhp1["host"],rhp1["port"])
      elif sys.argv[1][0]=="v":
        c = remote(rhp3["host"],rhp3["port"])
    else:
        c = remote(rhp2['host'],rhp2['port'])
    exploit()
    c.interactive()
```


# アウトロ
楽しかったです。
課題が終わりません。
ぴえん。

# 参考
Python公式のドキュメント
https://docs.python.org/3/library/re.html
自分のブログ
https://smallkirby.hatenablog.com/entry/2020/11/30/233722
ニルギリ
https://www.youtube.com/watch?v=yvUvamhYPHw

