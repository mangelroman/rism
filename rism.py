import os
import sys
import argparse

from lxml import etree
import xmltodict
import re
import numpy as np
import multiprocessing as mp

from pathlib import Path
from tqdm import tqdm
from itertools import cycle
from midi import get_midi_instrument, get_midi_instrument_name
from pae import clean_pae

class Counters(object):
    def __init__(self, size=1):
        manager = mp.Manager()
        self.count_dict = manager.dict()
        self.lock = mp.Lock()

    def increment(self, key):
        with self.lock:
            if key not in self.count_dict:
                self.count_dict[key] = 0
            self.count_dict[key] += 1

    def value(self, key):
        return self.count_dict[key]

    def values(self):
        return self.count_dict

def parseRange(string):
    m = re.match(r'(\d+):(\d+)', string)
    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected forms like '80:120'")
    return [int(m[1]), int(m[2])]

parser = argparse.ArgumentParser(description='RISM database preparation')
parser.add_argument('--data-dir', metavar='DIR', help='path to data', required=True)
parser.add_argument('--num-workers', default=None, type=int, help='Number of workers used in data preparation')
parser.add_argument('--length', type=int, default=1118949, help='Number of RISM incipits')
parser.add_argument('--tempo-range', type=parseRange, help='Select tempo ranges in the format start:end', default='80:120')
parser.add_argument('xml', metavar='FILE', help='Path to RISM XML database')

def process_record(record, tempos, args, counters):
    record = record['marc:record']
    record_id = None
    for cf in record['marc:controlfield']:
        if cf['@tag'] == '001':
            record_id = cf.get('#text')
            break
    if record_id is None or not record_id.isdigit():
        return

    counters.increment('records')
    tempoit = cycle(tempos)

    for df in record['marc:datafield']:
        if df['@tag'] == '031':
            paedata = clef = timesig = keysig = None
            i1 = i2 = i3 = None
            key= instrument = None
            for sf in df['marc:subfield']:
                if sf['@code'] == 'a':
                    i1 = sf.get('#text')
                elif sf['@code'] == 'b':
                    i2 = sf.get('#text')
                elif sf['@code'] == 'c':
                    i3 = sf.get('#text')
                elif sf['@code'] == 'g':
                    clef = sf.get('#text')
                elif sf['@code'] == 'n':
                    keysig = sf.get('#text')
                elif sf['@code'] == 'o':
                    timesig = sf.get('#text')
                elif sf['@code'] == 'r':
                    key = sf.get('#text')
                elif sf['@code'] == 'm':
                    instrument = sf.get('#text')
                elif sf['@code'] == 'p':
                    paedata = sf.get('#text')
            if paedata is None or clef is None or timesig is None:
                continue
            if i1 is None or i2 is None or i3 is None:
                continue
            if not i1.isdigit() or not i2.isdigit() or not i3.isdigit():
                continue

            counters.increment('incipits')
            paedict = {}
            paedict['@start'] = f'{record_id}-{i1}_{i2}_{i3}'
            paedict['@clef'] = clef
            paedict['@keysig'] = keysig if keysig is not None else ''
            paedict['@timesig'] = timesig
            paedict['@key'] = key if key is not None else ''
            paedict['@instrument'] = instrument if instrument is not None else ''
            paedict['@data'] = paedata
            paedict['@end'] = paedict['@start']

            paedict = clean_pae(paedict)

            if paedict is None:
                continue

            counters.increment('valid')

            pae = ''
            for k, v in paedict.items():
                pae += f'{k}:{v}\n'

            root = Path(args.data_dir) / record_id[:-5] / record_id[-5:]
            root.mkdir(parents=True, exist_ok=True)

            paefile = root / str(paedict['@start'] + '.pae')
            paefile.write_text(pae)

            try:
                kernfile = paefile.with_suffix('.krn')
                status = os.system(f'pae2kern -e krn -d {str(root)}/ {str(paefile)} >/dev/null 2>&1')
                if (os.WEXITSTATUS(status) != 0):
                    raise OSError("pae2kern")
                midifile = paefile.with_suffix('.mid')                
                tempo = next(tempoit)
                midi_inst = get_midi_instrument(paedict['@instrument'])
                counters.increment(midi_inst)
                status = os.system(f'hum2mid {str(kernfile)} -C -v 100 -t {tempo/100.0} -f {midi_inst} -o {str(midifile)} >/dev/null 2>&1')
                if (os.WEXITSTATUS(status) != 0):
                    raise OSError("hum2mid")
            except OSError as e:
                print(f"Error while running {e} on file {paefile}")
                paefile.unlink()
                if kernfile.exists():
                    kernfile.unlink()
                if midifile.exists():
                    midifile.unlink()
                root.rmdir()
            else:
                counters.increment('converted')


def process_rism(q, args, counters):
    while True:
        item = q.get()
        if item is None:
            break
        process_record(item[0], item[1], args, counters)

if __name__ == '__main__':
    args = parser.parse_args()

    print("Converting dataset:")
    sys.stdout.flush()

    if args.num_workers is None:
        args.num_workers = mp.cpu_count()

    q = mp.Queue(maxsize=args.num_workers)
    counters = Counters()
    pool = mp.Pool(args.num_workers, initializer=process_rism, initargs=(q, args, counters))
    parser = etree.iterparse(args.xml, tag='{http://www.loc.gov/MARC21/slim}record', events=('end', ))
    np.random.seed(44)
    for event, element in tqdm(parser, total=args.length, ascii=True):
        record = xmltodict.parse(etree.tostring(element))
        tempos = np.random.randint(low=args.tempo_range[0], high=args.tempo_range[1] + 1, size=10)
        q.put((record, tempos))
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]
        #for ancestor in element.xpath('ancestor-or-self::*'):
        #    while ancestor.getprevious() is not None:
        #        del ancestor.getparent()[0]
    del parser

    # stop workers
    for i in range(args.num_workers):
        q.put(None)

    pool.close()
    pool.join()

    print(f'Total valid records: {counters.value("records")}')
    print(f'Total PAE incipits: {counters.value("incipits")}')
    print(f'Total valid incipits: {counters.value("valid")}')
    print(f'Total kern/midi incipits: {counters.value("converted")}')
    
    print('Instrument distribution:')
    sorted_counters = dict(sorted(counters.values().items(), key=lambda x: x[1], reverse=True))
    for k,v in sorted_counters.items():
        if k not in ['records', 'incipits', 'valid', 'converted']:
            name = get_midi_instrument_name(k)
            print(f'{v:10d} {name}({k})')
    sys.exit(0)
