# MAD -- Malicious Application Detector

## Before you start

### Prerequisites

#### System requirements

- Ubuntu 16.04
- run with `root` privilege
- preferred using `docker` & `docker-compose`

#### Software & Libraries

- `libpcap`
- [`pkt2flow`](https://github.com/caesar0301/pkt2flow)
- MySQL 5.7
- CPython 3.5+
- [`shodan`](https://www.shodan.io) API token

#### Python dependencies

- `Django`
- `dpkt`
- `peewee`
- `PyMySQL`
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

#### Develop Environment

```bash
git clone https://github.com/JarryShaw/mad.git
cd mad
# omit docker tags (default is <latest>)
./build.sh
# with certain tags (e.g. v0.1b1)
./build.sh "v0.1b1"
```

#### Distribution Environment

1. Modify `{app,gem,www}/init.sh` if you need;
2. Modify `docket-compose.yml` if you need;
3. Run `./init.sh volumes` to create directories;
4. Run `./init.sh archives` to set up CNN models and retrain dataset;
5. Run `docker-compose up --build -d` to start up MAD services in detach mode.

## Configurations (for Docker Compose only)

### Automation

- [`init.sh`](init.sh)
  - `db` -- set up database tables
  - `model` -- set up CNN models (`/home/traffic/db/apt_model`)
  - `report` -- set up report directory (`/home/traffic/db/apt_report`)
  - `retrain` -- set up retrain dataset (`/home/traffic/db/apt_retrain`)
  - `dataset` -- set up dataset directory (`./log/dataset`)
  - `volumes` -- set up shared directories, i.e. `report` & `dataset`
  - `archives` -- set up archives, i.e. `model` & `retrain`
  - `all` -- set up all stuff, i.e. `retrain` & `model` & `report` & `dataset` & `db`
- [`cleanup.sh`](cleanup.sh)
  - `db` -- reset database
  - `log` -- empty log (`/home/traffic/pcapfile/apt_log.txt`)
  - `model` -- reset CNN models (`/home/traffic/db/apt_model`)
  - `report` -- remove reports (`/home/traffic/db/apt_report`)
  - `dataset` -- remove datasets (`./log/dataset`)
  - `retrain` -- reset retrain dataset (`/home/traffic/db/apt_retrain`)
  - `volumes` -- cleanup shared directories, i.e. `report` & `dataset`
  - `archives` -- reset archives, i.e. `model` & `retrain`
  - `all` -- cleanup all stuff, i.e. `retrain` & `model` & `report` & `dataset` & `log` & `db`

### `mad_app` -- main application

- [`docker-compose.yml`](docker-compose.yml)
  - CPU usage
    - 50% of available CPUs
    - 75% of CPU processing shares
  - Memory usage
    - 96G memory limit
    - 192G `SWAP` limit
  - Volume path
    - PCAP sources (`/mad/pcap`) in `/home/traffic/pcapfile`
    - dataset directory (`/mad/dataset`) in `./log/dataset`
    - CNN models (`/mad/model`) in `/home/traffic/db/apt_model`
    - retrain dataset (`/mad/retrain`) in `/home/traffic/db/apt_retrain`
- [`init.sh`](app/init.sh)
  - Sample source: `/mad/pcap`
  - Rounds interval: `0s`
  - Sampling interval: `0`
  - Validation ratio: `10%`
  - Process number: `15`
  - `MEMLOCK` limit: `unlimited`
  - `VMEM` limit: `unlimited`
  - `AS` limit: `unlimited`
  - `SWAP` limit: `unlimited`
  - Validation: `yes`
  - Develop mode: `no`

### `mad_gen` -- report generator

- [`docker-compose.yml`](docker-compose.yml)
  - Volume path
    - report directory (`/mad/report`) in `/home/traffic/db/apt_report`
    - dataset directory (`/mad/dataset`) in `./log/dataset`
- [`init.sh`](gen/init.sh)
  - Cleanup reports: `yes`
  - Process number: `4`
  - Sleep interval: `5m`
  - API token: `6JJ0qCCNHzv6iLsPvUPQNst0Dpbh87io`

### `mad_www` -- web dashboard

- [`docker-compose.yml`](docker-compose.yml)
  - Volume path
    - report directory (`/mad/report`) in `/home/traffic/db/apt_report`
- [`init.sh`](www/init.sh)

### `mad_db` -- MySQL database

- [`docker-compose.yml`](docker-compose.yml)
  - Volume path
    - initialisation script (`/docker-entrypoint-initdb.d`) in [`sql/MySQL.sql`](sql/MySQL.sql)
    - database library (`/var/lib/mysql`) in `/home/traffic/db/apt_db`

## Entry points

### CLI

#### Main Application

```text
$ python run_mad.py --help
usage: mad_app [-h] [-V] [-m {1,2,3,4,5}] [-p DIR] [-s FILE] [-n] [-o SEC]
               [-t INT] [-r PCT] [-c PROC] [-l MEM] [-v MEM] [-a MEM] [-w MEM]
               [-d] [-i] [-e SHELL]

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
  -r PCT, --validate-ratio PCT
                        validate %PCT% percent of CNN detection results
                        (mode=3; default is 10)

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

#### Report Generator

```text
$ python3 generate_report.py --help
usage: mad_gen [-h] [-c] [-f] [-i SEC] [-p NUM] [-t KEY]

positional arguments:
  -t, --token           shodan.io API token

optional arguments:
  -h, --help            show this help message and exit
  -c, --cleanup         remove processed CNN reports
  -f, --force-cleanup   remove CNN reports regardless of processing error
  -i, --interval        sleep interval between rounds
  -p, --process         process number (default is %log2(CPU)%)
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
│   ├── jsonutil.py
│   └── webgraphic                  # WebGraphic filtering algo.
│       ├── group.py
│       ├── top-10k.txt
│       └── webgraphic.py
├── bootstrap.sh
├── build.sh
├── cleanup.sh
├── cleanup.sql
├── docker-compose.yml
├── docker.sh
├── gen                             # report generator
│   ├── SQLManager                  # database interfaces
│   │   ├── Model.py
│   │   └── __init__.py
│   ├── generate_report.py          # main module
│   ├── generator.py                # generators
│   ├── init.sh                     # entry point
│   ├── jsonutil.py
│   └── server_map.py               # generator for server_map.json
├── init.sh
├── make.sh
├── model.tar.gz
├── retrain.tar.gz
├── sql                             # database utility
│   └── MySQL.sql                   # MySQL initialisation script
├── www                             # web dashboard implementation
    ├── init.sh                     # entry point
    ├── mad
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── templates
    │   │   ├── pages
    │   │   │   ├── connection.html
    │   │   │   ├── index.html
    │   │   │   ├── innerIp.html
    │   │   │   ├── inner_detail.html
    │   │   │   ├── more.html
    │   │   │   ├── outerIp.html
    │   │   │   ├── outer_detail.html
    │   │   │   ├── ua.html
    │   │   │   └── ua_detail.html
    │   │   └── static
    │   │       ├── dist
    │   │       │   ├── css
    │   │       │   │   ├── animate.css
    │   │       │   │   ├── filter.css
    │   │       │   │   ├── font-awesome.min.css
    │   │       │   │   ├── lightgallery.css
    │   │       │   │   ├── linea-icon.css
    │   │       │   │   ├── material-design-iconic-font.min.css
    │   │       │   │   ├── pe-icon-7-stroke.css
    │   │       │   │   ├── pe-icon-7-styles.css
    │   │       │   │   ├── simple-line-icons.css
    │   │       │   │   ├── style.css
    │   │       │   │   └── themify-icons.css
    │   │       │   ├── fonts
    │   │       │   │   ├── fontawesome
    │   │       │   │   │   ├── fontawesome-webfont.woff
    │   │       │   │   │   └── fontawesome-webfont.woff2
    │   │       │   │   ├── simple-line-icons
    │   │       │   │   │   └── Simple-Line-Icons4c82.ttf
    │   │       │   │   ├── themify-icons
    │   │       │   │   │   └── themify.woff
    │   │       │   │   └── themify.ttf
    │   │       │   └── js
    │   │       │       ├── dataTool.min.js
    │   │       │       ├── download.js
    │   │       │       ├── dropdown-bootstrap-extended.js
    │   │       │       ├── echarts.min.js
    │   │       │       ├── index
    │   │       │       │   └── init.js
    │   │       │       ├── index_data.js
    │   │       │       ├── index_init.js
    │   │       │       ├── index_map.js
    │   │       │       ├── inner_detail.js
    │   │       │       ├── jquery.slimscroll.js
    │   │       │       ├── outer_detail.js
    │   │       │       └── ua_detail.js
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
    │   │           │   ├── bootstrap
    │   │           │   │   └── dist
    │   │           │   │       ├── css
    │   │           │   │       │   └── bootstrap.min.css
    │   │           │   │       ├── fonts
    │   │           │   │       │   ├── glyphicons-halflings-regular.woff
    │   │           │   │       │   └── glyphicons-halflings-regular.woff2
    │   │           │   │       └── js
    │   │           │   │           └── bootstrap.min.js
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
    │   │           │   ├── jquery
    │   │           │   │   └── dist
    │   │           │   │       └── jquery.min.js
    │   │           │   ├── jquery-toast-plugin
    │   │           │   │   └── dist
    │   │           │   │       └── jquery.toast.min.js
    │   │           │   ├── jquery.counterup
    │   │           │   │   └── jquery.counterup.min.js
    │   │           │   ├── jszip
    │   │           │   │   └── dist
    │   │           │   │       └── jszip.min.js
    │   │           │   ├── morris.js
    │   │           │   │   ├── morris.css
    │   │           │   │   └── morris.min.js
    │   │           │   ├── owl.carousel
    │   │           │   │   └── dist
    │   │           │   │       ├── assets
    │   │           │   │       │   ├── owl.carousel.min.css
    │   │           │   │       │   └── owl.theme.default.min.css
    │   │           │   │       └── owl.carousel.min.js
    │   │           │   ├── pdfmake
    │   │           │   │   └── build
    │   │           │   │       ├── pdfmake.min.js
    │   │           │   │       └── vfs_fonts.js
    │   │           │   ├── raphael
    │   │           │   │   └── raphael.min.js
    │   │           │   └── switchery
    │   │           │       └── dist
    │   │           │           ├── switchery.min.css
    │   │           │           └── switchery.min.js
    │   │           ├── jquery.sparkline
    │   │           │   └── dist
    │   │           │       └── jquery.sparkline.min.js
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
    |   |-- fingerprint.pickle                  # pickled fingerprint database
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

## Licensing

This software and associated documentation files (the "Software") are
generally licensed under the [GNU GPLv3 License](LICENSE). The original
development branch of the MAD project as hosted on
[GitHub](https://github.com/JarryShaw/mad)) is licensed under the
[GNU GPLv3 License](LICENSE). The [`f2format`](https://github.com/JarryShaw/f2format)
transformed distribution branch, as hosted on [GitLab](http://gitlab.opensdns.com/contest/apt),
is licensed under the
<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">
Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License
</a>. No permits are foreordained unless granted by the authors and
maintainers of the Software.
