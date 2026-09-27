"""Predeclared modern MIPLIB selection; original files and hashes retained."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,urllib.request,urllib.parse,ssl
try:
    import certifi
    TLS=ssl.create_default_context(cafile=certifi.where())
except ImportError:
    TLS=ssl.create_default_context()
ROOT=Path(__file__).resolve().parents[1]
SELECTION=['markshare_4_0','blend2','binkar10_1']
def main():
    folder=ROOT/'datasets/miplib2017';folder.mkdir(parents=True,exist_ok=True);records=[]
    for name in SELECTION:
        page=f'https://miplib.zib.de/instance_details_{name}.html'
        record={'name':name,'details':page}
        try:
            html=urllib.request.urlopen(page,timeout=30,context=TLS).read().decode()
            links=re.findall(r'href=[\"\']([^\"\']+\.mps\.gz)[\"\']',html)
            if not links:raise RuntimeError('No official MPS download link found')
            url=urllib.parse.urljoin(page,links[0]);raw=folder/(name+'.mps.gz')
            if not raw.exists():raw.write_bytes(urllib.request.urlopen(url,timeout=45,context=TLS).read())
            data=raw.read_bytes();model=gzip.decompress(data)
            if b'ENDATA' not in model:raise RuntimeError('Invalid downloaded MPS')
            (folder/(name+'.mps')).write_bytes(model)
            record.update(url=url,status='downloaded',raw_sha256=hashlib.sha256(data).hexdigest(),model_sha256=hashlib.sha256(model).hexdigest())
        except Exception as error:record.update(status='download_failed',error=str(error))
        records.append(record);print(name,record['status'],flush=True)
    (folder/'manifest.json').write_text(json.dumps({'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':SELECTION,'instances':records},indent=2)+'\n')
if __name__=='__main__':main()
