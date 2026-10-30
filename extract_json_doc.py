import zipfile,re,html
p=r'D:\网络安全\json.docx'
s=zipfile.ZipFile(p).read('word/document.xml').decode()
s=re.sub(r'</w:p>','\n',s); s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
open('json_extract.txt','w',encoding='utf8').write(s)
print('S001 count',s.count('"sample_id":"S001"')+s.count('"sample_id": "S001"'))
print('length',len(s))
