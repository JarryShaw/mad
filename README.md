# MAD -- Malicious Application Detector

## Before you start

### Prerequisites

#### System requirements

- Ubuntu 16.04
- run as `root` privilege
- preferred using `docker`

#### Software & Libraries

- `libpcap`
- [`pkt2flow`](https://github.com/caesar0301/pkt2flow)
- CPython 3.5+
- MySQL (name set to be `mad_db`)
- [`shodan`](https://www.shodan.io) API token

#### Python dependencies

- `Django`
- `dpkt`
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

```
$ python run_mad.py --help
usage: mad [-h] [-V] [-m {1,2,3,4,5}] [-p DIR] [-s FILE] [-n] [-t INT]
           [-c PROC] [-l MEM] [-v MEM] [-a MEM] [-w MEM] [-d] [-i] [-e SHELL]

Malicious Application Detector

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit

general arguments:
  -m {1,2,3,4,5}, --mode {1,2,3,4,5}
                        runtime mode
  -p DIR, --path DIR    input file name or directory (mode=1/2/3)
  -s FILE, --sample FILE
                        sample file(s) for model training (mode=2/5)

runtime arguments:
  -n, --no-validate     do not run validate process after prediction (mode=3)
  -o SEC, --wait-timeout SEC
                        wait for %SEC% seconds between each round (mode=3;
                        default is 0)
  -t INT, --sampling-interval INT
                        sample every %INT% file(s) (mode=3; default is 0, i.e.
                        sampling from all files)

resource arguments:
  -c PROC, --process PROC
                        number of concurrent processes that may run (default
                        is %log2(CPU)%)
  -l MEM, --memlock MEM
                        number of bytes of memory that may be locked into RAM
                        (default is %MEMLOCK%)
  -v MEM, --vmem MEM    largest area of mapped memory which the process may
                        occupy (default is %VMEM%)
  -a MEM, --address-space MEM
                        maximum area (in bytes) of address space which may be
                        taken by the process (default is %AS%)
  -w MEM, --swap MEM    maximum size (in bytes) of the swap space that may be
                        reserved or used by all of this user id's processes
                        (default is %SWAP%)
  -n, --no-validate     do not run validate process after prediction (mode=3)

development arguments:
  -d, --devel           run in develop mode (quit after first round)
  -i, --interactive     enter interactive mode (running SHELL)
  -e SHELL, --shell SHELL
                        shell for interactive mode (default is '/bin/sh')
```

### API

```python
from mad import main
main(mode=3, path='/mad/pcap', sample=None)
```

#### Args

```text
iface - str, network interface for sniffing (mode=1) c.f. scapy.all.sniff (deprecated)
mode - int, runtime mode
    |-- 1 -> initialisation
    |-- 2 -> migration
    |-- 3 -> prediction -- the main course （default)
    |-- 4 -> adaptation -- retain the models
    |-- 5 -> regeneration -- dev only
path - str, input file name or directory (mode=1/2)
file - str, JSON file name w/ list of input file names (mode=3) (deprecated)
sample - str, path of training sample(s) (mode=2, 5)
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

```text
/
├── Dockerfile
├── Pipfile
├── README.md
├── app                             # core app implementation
│   ├── DataLabeler                 # labeller using VT
│   │   ├── DataLabeler.py
│   │   ├── VirusTotal3.py
│   │   ├── VirusTotalThread.py
│   │   └── proxies3.txt
│   ├── SQLManager                  # database interfaces
│   │   ├── Model.py
│   │   └── __init__.py
│   ├── StreamManager               # generate stream PCAP files
│   │   └── StreamManager4.py
│   ├── Training.py                 # CNN
│   ├── fingerprints                # fingerprint generator & manager
│   │   ├── LevenshteinDistance.py
│   │   ├── detection.py
│   │   ├── fingerprint.py
│   │   └── fingerprintsManager.py
│   ├── init.sh                     # entry point
│   ├── mad.py                      # main entry point
│   ├── make_stream.py              # generate stream info dict
│   ├── run_mad.py                  # CLI entry point
│   ├── utils.py
│   └── webgraphic                  # WebGraphic filtering algo.
│       ├── group.py
│       ├── top-10k.txt
│       └── webgraphic.py
├── bootstrap.sh
├── build.sh
├── docker-compose.yml
├── docker.sh
├── gen                             # report generator
│   ├── generate_report.py          # main module
│   ├── SQLManager                  # database interfaces
│   │   ├── Model.py
│   │   └── __init__.py
│   └── init.sh                     # entry point
├── make.sh
├── model.tar.gz
├── retrain.tar.gz
├── sql                             # database utility
│   └── MySQL.sql                   # MySQL initialisation script
└── www                             # web dashboard implementation
    ├── init.sh                     # entry point
    ├── mad
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── templates
    │   │   ├── pages
    │   │   │   ├── index.html
    │   │   │   ├── index_old.html
    │   │   │   ├── inner_detail.html
    │   │   │   ├── inner_detail_old.html
    │   │   │   ├── more.html
    │   │   │   ├── more_old.html
    │   │   │   ├── outer_detail.html
    │   │   │   ├── outer_detail_old.html
    │   │   │   ├── ua_detail.html
    │   │   │   └── ua_detail_old.html
    │   │   └── static
    │   │       ├── files
    │   │       │   └── 基于流量的自反馈恶意软件监测系统.pdf
    │   │       ├── img
    │   │       │   ├── System.png
    │   │       │   ├── favicon.ico
    │   │       │   ├── favicon.png
    │   │       │   ├── logo.png
    │   │       │   ├── sidebar1.jpg
    │   │       │   ├── sliderImg1.jpg
    │   │       │   ├── sliderImg2.jpg
    │   │       │   ├── sliderImg3.jpg
    │   │       │   └── sliderImg4.jpg
    │   │       └── vendors
    │   │           ├── bower_components
    │   │           │   ├── awesome-bootstrap-checkbox
    │   │           │   │   └── awesome-bootstrap-checkbox.css
    │   │           │   ├── datatables
    │   │           │   │   └── media
    │   │           │   │       ├── css
    │   │           │   │       │   └── jquery.dataTables.min.css
    │   │           │   │       └── js
    │   │           │   │           └── jquery.dataTables.min.js
    │   │           │   ├── datatables.net-buttons
    │   │           │   │   └── js
    │   │           │   │       ├── buttons.flash.min.js
    │   │           │   │       ├── buttons.html5.min.js
    │   │           │   │       ├── buttons.print.min.js
    │   │           │   │       └── dataTables.buttons.min.js
    │   │           │   ├── jquery.counterup
    │   │           │   │   └── jquery.counterup.min.js
    │   │           │   ├── morris.js
    │   │           │   │   ├── morris.css
    │   │           │   │   └── morris.min.js
    │   │           │   └── raphael
    │   │           │       └── raphael.min.js
    │   │           └── vectormap
    │   │               ├── jquery-jvectormap-2.0.2.css
    │   │               ├── jquery-jvectormap-2.0.2.min.js
    │   │               ├── jquery-jvectormap-au-mill.js
    │   │               ├── jquery-jvectormap-in-mill.js
    │   │               ├── jquery-jvectormap-uk-mill-en.js
    │   │               ├── jquery-jvectormap-us-aea-en.js
    │   │               └── jquery-jvectormap-world-mill-en.js
    │   ├── urls.py
    │   └── views.py
    ├── manage.py
    └── www
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
```

## Report directory

```text
/mad/
    |-- mad.log                                 # log file for RPC (0-start; 1-stop; 2-retrain; 3-ready; 4-error)
    |-- fingerprint.pickle                      # pickled fingerprint database
    |-- pcap/
    |   |-- apt_log.txt                         # log file
    |   |-- YYYY_MMDD_HHMM_SS.pcap              # PCAP files
    |   |-- ...
    |-- dataset/                                # where all dataset go
    |   |-- YYYY-MM-DDTHH:MM:SS.US/             # dataset named after ISO timestamp
    |   |   |-- groups.json                     # WebGraphic group record
    |   |   |-- filter.json                     # fingerprint filter report
    |   |   |-- record.json                     # flattened group record
    |   |   |-- report.json                     # detection report
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
    |-- model/                                  # where CNN model go
    |   |-- Background_PC/                      # Background_PC models
    |   |   |-- ...
    |   |-- ...
    |-- report/                                 # where generated reports go
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
repo hosting on [GitLab](http://gitlab.opensdns.com/contest/apt). Then run
`f2format` command to make them Python 3.5 compatible. Afterwards, it shall
upload both repositories to where it belongs.

## License

This work (original development branch of the MAD project as hosted on
[GitHub](https://github.com/JarryShaw/mad)) is licensed under
[GNU GPLv3](LICENSE). The `f2format` transformed distribution branch, as hosted
on [GitLab](http://gitlab.opensdns.com/contest/apt), is licensed under a
<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">
Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License
</a>.
