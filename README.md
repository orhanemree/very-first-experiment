# Very First Experiment
My very first time writing computer-based psychology experiments using `PsychoPy`.

## Tasks Implemented
Each task has its own folder consisting of README, implementation (`main.py`) and sample run files. See READMEs for task details and sample results.
- [x] [Sternberg](/sternberg/README.md): working memory
- [x] [Auditory N-Back](/auditory_n_back/README.md): working memory update

## Quick Start
Since `PsychoPy` is not compatible with the latest `Python` version, I used `Python=3.10` and `PsychoPy=2026.2.1` versions.
* Clone repository.
```bash
$ git clone https://github.com/orhanemree/very-first-experiment.git
$ cd very-first-experiment
```
* Create specified virtual environment and install `PsychoPy`.
```bash
$ python3.10 -m venv .venv
$ source .venv/bin/activate # activate venv depending on your OS
$ pip install psychopy==2026.2.1
```
* You can now run a sample task. Run a file as a module. For example, run Sternberg sample:
```bash
$ python3.10 -m sternberg.sample
```

## Papers
Papers that inspired these experiments are listed in each task's README.

## License
MIT