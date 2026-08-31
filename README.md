# Very First Experiment
My very first time writing computer-based psychology experiments using `PsychoPy`.

## Quick Start
`PsychoPy` is not compatible with the latest `Python` version. I used `Python=3.10` and `PsychoPy=2026.2.1` versions.
* Clone repository and set up specified environment. Then:
```bash
cd very-first-experiment
pip install psychopy==2026.2.1
```
* Run files as a module. For example to run sample Sternberg Task:
```bash
python3.10 -m sternberg.run
```

## Tasks Implemented
Each task has its own folder consisting of README, implementation (i.e., `main.py`) and sample runs (e.g., `run.py`). See READMEs for task details and sample results.
- [x] [Sternberg](/sternberg/README.md): working memory
- [ ] Auditory n-back: working memory update

## Papers
Papers that inspired these experiments are listed in each task's README.

## License
MIT