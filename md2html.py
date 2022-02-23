#!/usr/bin/env python
#encoding: utf-8;

'''
Markdown to HTML converter for blog

- 変換表 --------------
# -> <h3></h3>
## -> <h4></h4>
### -> <h5></h5>
#### -> <h6></h6>

```test.c
write code here
``` -> <pre class="prettyprint linenums"></pre>

通常の文章 -> <p></p>
末尾に2個以上のスペース -> <br>
**hoge** -> <strong>hoge</strong>
*hoge* -> <em>hoge</em>
***hoge*** -> <strong><em>hoge</em></strong>
> hoge -> <blockquote><p>hoge</p></blockquote>

[content](URL) -> <a href=URL>content</a>
'''

from io import IncrementalNewlineDecoder
import sys
import os
import re
import argparse
import html

header_content = '''
<p><script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js?skin=desert"></script></p>
{} <!-- KEYWORDS HERE -->
<div class="contents">[:contents]</div>
<p> </p>
<p> </p>
'''
keywords_template = '''
<div class="keywords"><span class="btitle">keywords</span>
<p>{}</p>
</div>
'''

pp_title = '''
<div style="margin-bottom:0; padding-bottom:0; display:inline; font-size:80%; background-color:#3d3939;">{}</div>
'''

footer_content = '''
<p></p><p></p>
<p></p><p></p>
<p>続く...</p>
<p></p><p></p>
'''

headers = [
  [r'^#### (.*)$', "<h6>", "</h6>"],
  [r'^### (.*)$', "<h5>", "</h5>"],
  [r'^## (.*)$', "<h4>", "</h4>"],
  [r'^# (.*)$', "<h3>", "</h3>"],
]

bi = [
  [r'(\*\*\*(.*?)\*\*\*)', " <strong><em>", "</em></strong> "],
  [r'(\*\*(.*?)\*\*)', " <strong>", "</strong> "],
  [r'(\*(.*?)\*)', " <em>", "</em> "],
]

codeblock = [
  r'^```(.*)' , '<pre class="prettyprint linenums {}">', '</pre>'
]

inlinecode = [
  r'`(.*?)`', '<code>', '</code>'
]

urlref = [
  r'\[(.*?)\]\((.*?)\)', '<a href="{}">', '</a>'
]

hackmd_img = r'^\!\['

def genPrettyprintArgs(filename):
  result = re.findall(r'(.*)\.(.*)', filename)
  if result == []:
    return ""
  else:
    return "lang-{}".format(result[0][1])

class Nirugiri:
  def __init__(self):
    self.ilines = []
    self.olines = []
    self.inCodeblock = False
    self.headerFound = False
    self.rules = [headers]
    self.section_number = 1
    self.now_reference = False
    self.codename = ""

  def readfile(self, filename):
    try:
      with open(filename, "r") as f:
        self.ilines = f.readlines()
      self.ilines = list(map(html.escape, self.ilines))
      self.filename = filename
      return True
    except(FileNotFoundError):
      print("File not found: "+sys.argv[1])
      return False

  def handle_reference(self, lines):
    self.olines.append("<h3>{}: References</h3>\n".format(self.section_number))
    a_template = "<p><a href='{}'>{}</a></p>\n"
    for i in range(len(lines)//2):
      title = lines[i*2].rstrip()
      ref = lines[i*2 + 1].rstrip()
      self.olines.append("<p>{}: {}</p>\n".format(str(i+1), title))
      self.olines.append(a_template.format(ref, ref))

  def parse(self):
    # keywords
    kstr = keywords_template
    if "keywords" in self.ilines[0]:
      i = 0
      keywords = ""
      for k in self.ilines[1].split(","):
        keywords += k
        if i < len(self.ilines[1].split(","))-1:
          keywords += " / "
        i += 1
      kstr = kstr.format(keywords)
    else:
      kstr = ""

    self.ilines = self.ilines[2:]

    # header
    self.olines.append(header_content.format(kstr))

    # content
    for i_line, l in enumerate(self.ilines):
      # check if reference
      if l.rstrip() == "# References":
        self.now_reference = True
        self.handle_reference(self.ilines[i_line+1:])
        break

      # start/end of codeblock (must be at end of parse())
      result = re.match(codeblock[0], l)
      if result != None:
        if not self.inCodeblock:
          self.inCodeblock = True
          if len(result.groups()[0]) >= 1:
            self.codename = result.groups()[0]
          if self.codename!=None and len(self.codename)>=1:
            self.olines.append(pp_title.format(self.codename))
          self.olines.append(codeblock[1].format(genPrettyprintArgs(self.codename)) + "\n")
        else:
          self.inCodeblock = False
          self.codename = ""
          self.olines.append(codeblock[2] + "\n")
        continue

      if not self.inCodeblock: # not in codeblock
        # ignore imgr image
        if len(re.findall(hackmd_img, l)) > 0:
          l = ""

        # header
        for i, r in enumerate(headers):
          if not self.headerFound:
            result = re.match(r[0], l)
            if result != None:
              if i == 3: # <h3>
                self.olines.append(r[1] + "{}: ".format(self.section_number) + result.groups()[0] + r[2] + "\n")
                self.section_number += 1
              else:
                self.olines.append(r[1] + result.groups()[0] + r[2] + "\n")
              self.headerFound = True
        if self.headerFound:
          self.headerFound = False
          continue

        # bold, italic
        for r in bi:
          result = re.findall(r[0], l)
          if len(result) > 0:
            for p in result:
              l = l.replace(p[0], r[1] + p[1] + r[2])

        # inline
        result = re.findall(inlinecode[0], l)
        if len(result) > 0:
          for p in result:
            l = l.replace('`'+p+'`', inlinecode[1] + p + inlinecode[2])

        # URL ref
        result = re.findall(urlref[0], l)
        if len(result) > 0:
          for p in result:
            l = l.replace('['+p[0]+']('+p[1]+')', urlref[1].format(p[1]) + p[0] + urlref[2])

        # end
        self.olines.append("<p>" + l.rstrip() +"</p>" + "\n")

      else: # in codeblock
        self.olines.append(l)

    # footer
    self.olines.append(footer_content)


  def output(self, force):
    filename = self.filename[:-3] + ".html"
    if (not force) and os.path.exists(filename):
      print("Error: file already exists: {}".format(filename))
      return False
    with open(filename, "w") as f:
      f.writelines(self.olines)
    print("Output: " + filename)
    return True



def usage():
  print("Markdown to HTML converter for kirby's blog")
  print("------------------------------------------------")
  print("Usage: {} <markdown file>".format(sys.argv[0]))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('mdfile', help='MD file to covert')
  parser.add_argument('-f', '--force', action='store_true', help='Force overwriting')
  parser.add_argument('--hackmd', action='store_true', help='Use HackMD syntax')
  args = parser.parse_args()
  mdname = args.mdfile
  force = args.force
  ishackmd = args.hackmd

  if len(mdname) <= 0:
    usage()
    exit(0)

  n = Nirugiri()
  if n.readfile(mdname) == False:
    exit(0)

  if n.parse() == False:
    exit(0)

  if n.output(force) == False:
    exit(0)

