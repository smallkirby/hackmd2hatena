keywords
heap, tcache, realloc, double free, size confusion, 小ネタ

# イントロ
最近、CTFを完全に辞めて、競プロをやることにしました。前から競プロできるひとかっこいいなぁと思っていたのですが、直接の動機はこの前のHITCONの問題でした。ここでダイクストラを使ったカーネルモジュールが出題されたのですが、アルゴリズム全然知らんマンなのでやる気がなくなってコードが読めませんでした。もともと数学は誇張抜きに小学3年生くらいしかできない(小学校は大部分行ってなかったので実質幼稚園並にしかできない)ので、それを克服するためにも頑張りたいです。
さてさて、ということで、今回は**realloc**を使った **tcache** double-freeに関する小さいお話を少し。**かなり古いネタ**ですが備忘録的に書き残しておきます。
また、最近 **glibc** にちょっとしたパッチを送ったのを契機にglibcのメーリスを読むようになったので、そこで議論になっていたtcacheの小ネタを書きます。


# reallocによるdouble-free/size-confusion
小学校で既に教わっていると思いますが、**glibc 2.29** 以降では **tcaceh** に **key** というメンバが加わっています。
*malloc()* する際にはここに *tcache*(*tcache_per_thread*構造体の方) の値が書き込まれ、*free()* 時にこのアドレスに *tcache* のアドレスが入っていればmemory corruptionとしてエラーにするというやつですね。というわけで最近のglibcにおいては単純に二回続けて *free()* することでdouble-freeを起こすということはできなくなっています。

但し、*realloc()* の場合には条件が揃うと簡単にtcacheを用いてmemory corruptionを引き起こすことができます。具体的には、以下の2つのことができます。
1. 複数のchunkを異なるサイズのtcacheに繋ぐことができる。
2. 1を用いて隣接するchunkをoverwriteできる。

## 方法

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

