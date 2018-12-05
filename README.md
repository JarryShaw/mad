# MAD -- Malicious Application Detector

## Before you start

### Prerequisites

#### System requirements

- run as `root`
- Ubuntu 16.04

#### Software & Libraries

- `libpcap`
- CPython 3.5+
- MySQL
- [`pkt2flow`](https://github.com/caesar0301/pkt2flow)

#### Python dependencies

- `Django`
- `dpkt`
- `geocoder`
- `peewee`
- `pymysql`
- `requests`
- `scapy`
- `tensorflow`
- `user-agents`

### Bootstrap installation

```bash
git clone https://github.com/JarryShaw/mad.git
cd mad
# build pkt2flow
./bootstrap.sh
# do not build pkt2flow
./bootstrap.sh "anything"  # just make sure $1 is not an empty string
```

### Docker distribution

```bash
git clone https://github.com/JarryShaw/mad.git
cd mad
# omit docker tags (default is <latest>)
./build.sh
# with certain tags (e.g. v0.1b1)
./build.sh "v0.1b1"
```

## Entry points

### CLI

```bash
$ python run_mad.py -h
usage: mad [-h] [-m {1,2,3,4,5}] [-i IFACE] [-p PATH] [-f FILE]

Malicious Application Detector

optional arguments:
  -h, --help            show this help message and exit
  -m {1,2,3,4,5}, --mode {1,2,3,4,5}
                        runtime mode
  -i IFACE, --iface IFACE
                        network interface for sniffing (mode=1) c.f.
                        scapy.all.sniff
  -p PATH, --path PATH  input file name or directory (mode=1/2)
  -f FILE, --file FILE  JSON file name w/ list of input file names (mode=3)
```

### API

```python
from mad import main
main(iface=None, mode=None, path=None, file=None)
```

#### Args

```text
iface - str, network interface for sniffing (mode=1) c.f. scapy.all.sniff
mode - int, runtime mode
    |-- 1 -> initialisation
    |-- 2 -> migration
    |-- 3 -> prediction -- the main course （default)
    |-- 4 -> adaptation -- retain the models
    |-- 5 -> regeneration -- dev only
path - str, input file name or directory (mode=1/2)
file - str, JSON file name w/ list of input file names (mode=3)
```

#### Returns

```python
None
```

## Examples

1. Start initialisation (`mode=1`) with all (legacy PCAP) files under `PATH`.

````python
>>> from mad import main
>>> main(mode=1, path=PATH)
````

2. Run migration (`mode=2`) with all (legacy PCAP) files from `PATH`, and start live prediction for `eth0` afterwards.

```python
>>> from mad import main
>>> main(mode=2, path=PATH, iface='eth0')
```

3. Run migration (`mode=2`) with all (legacy PCAP) files from `PATH`, and start prediction for PCAP files recorded in `FILE` (JSON list) afterwards.

```python
>>> from mad import main
>>> main(mode=2, path=PATH, file=FILE)
# FILE = 'data.json' -> ["foo.pcap", "bar.pcap", "boo.pcap", ...]
```

4. Directly run live prediction for `eth0`.

```python
>>> from mad import main
>>> main(mode=3, iface='eth0')
```

5. Directly run prediction for legacy PCAP files recorded in `FILE` (JSON list).

```python
>>> from mad import main
>>> main(mode=3, file=FILE)
# FILE = 'data.json' -> ["foo.pcap", "bar.pcap", "boo.pcap", ...]
```

## Repo directory

 > NB: `/retrain.tar.gz` contains files for retrain process, and should be extracted as `/usr/local/mad/retrain`

```text
/
├── app                             # core app implementation
│   ├── DataLabeler                 # labeller using VT
│   │   ├── DataLabeler.py
│   │   ├── VirusTotal3.py
│   │   ├── VirusTotalThread.py
│   │   └── proxies3.txt
│   ├── README.md
│   ├── StreamManager               # generate stream PCAP files
│   │   ├── StreamManager4.py
│   ├── Training.py                 # CNN
│   ├── fingerprints                # fingerprint generator & manager
│   │   ├── LevenshteinDistance.py
│   │   ├── detection.py
│   │   ├── fingerprint.py
│   │   ├── fingerprintsManager.py
│   ├── mad.py                      # main entry point
│   ├── run_mad.py                  # CLI entry point
│   ├── make_stream.py              # generate stream info dict
│   └── webgraphic                  # WebGraphic filtering algo.
│       ├── group.py
│       ├── top-10k.txt
│       └── webgraphic.py
└── www                             # web dashboard implementation
```

## Report directory

```text
/mad/
    |-- mad.log                                 # log file for RPC (0-start; 1-stop; 2-retrain; 3-ready)
    |-- fingerprint.pickle                      # pickled fingerprint database
    |-- dataset/                                # where all dataset go
    |   |-- YYYY-MM-DDTHH:MM:SS.US/             # dataset named after ISO timestamp
    |   |   |-- groups.json                     # WebGraphic group record
    |   |   |-- filter.json                     # fingerprint filter report
    |   |   |-- record.json                     # flattened group record
    |   |   |-- stream.json                     # backup for stream.json in retrain
    |   |   |-- tmp/                            # temporary files generated by pkt2flow
    |   |   |   |-- tcp_syn/
    |   |   |   |   |-- IP_PORT_IP_PORT_TS.pcap
    |   |   |   |   |-- ...
    |   |   |   |-- tcp_nosyn/
    |   |   |   |   |-- IP_PORT_IP_PORT_TS.pcap
    |   |   |   |   |-- ...
    |   |   |-- stream/                         # where stream files go
    |   |   |   |-- IP_PORT_IP_PORT_TS.pcap     # temporary stream PCAP files
    |   |   |   |-- ...
    |   |   |-- Background_PC/                  # where Background_PC dataset files go
    |   |       |-- 0/                          # clean ones
    |   |       |   |-- IP_PORT_IP_PORT_TS.dat  # dataset file
    |   |       |   |-- ...
    |   |       |-- 1/                          # malicious ones
    |   |           |-- IP_PORT_IP_PORT_TS.dat  # dataset file
    |   |           |-- ...
    |   |-- ...
    |-- report/                                 # where CNN prediction report go\
    |   |-- Background_PC/                      # Background_PC reports
    |   |   |-- index.json                      # report index file
    |   |   |-- YYYY-MM-DDTHH:MM:SS.US.json     # report named after dataset
    |   |-- ...
    |-- model/                                  # where CNN model go
    |   |-- Background_PC/                      # Background_PC models
    |   |   |-- ...
    |   |-- ...
    |-- retrain/                                # where CNN retrain data go
        |-- Background_PC/                      # Background_PC retrain dataset
        |   |-- 0/                              # clean ones
        |   |   |-- YYYY-MM-DDTHH:MM:SS.US_IP_PORT_IP_PORT_TS.dat
        |   |   |-- ...
        |   |-- 1/                              # malicious ones
        |       |-- YYYY-MM-DDTHH:MM:SS.US_IP_PORT_IP_PORT_TS.dat
        |       |-- ...
        |-- stream.json                         # stream index for retrain
```

## Contribution

When commit, use `./make.sh 'commit message'`. The script will automatically
retrieve useful files and copy them into `/apt` folder, which is the release
repo hosting on [GitLab](http://gitlab.opensdns.com/contest/apt.git). Then run
`f2format` command to make them Python 3.5 compatible. Afterwards, it shall
upload both repositories to where it belongs.
