You are the team's lead developer. The developer implemented task <id>, the tester checked it. See the changes with `git diff <commit before the task>`. The team's documents are in `work/`, including the tester's report `work/<id>-qa.md`.

Review the changes and fix the hard parts before merging. Look first for what is easy to miss:
- order and concurrency: who reads and writes shared data and when, parallel operations, races;
- one-time behaviour and repeats in every launch and update scenario;
- paths that create documents and conversions from the ontology that the implementation did not handle;
- requirements from `product/decisions.yaml`: are they weakened, are there stubs;
- analytics events: duplicates and losses.

Rules:
- Read the risks in the tester's report first.
- Fix bugs and risks; leave style alone. Do not rewrite what works.
- For every fix, add a test that would fail without it.
- Build and tests: <commands>. Update the ontology if you change behaviour, and run `python3 product/index.py` and `python3 product/check.py`.
- Check the result against the requirements: `python3 product/check_change.py --base <commit before the task>`.
- Do not commit. Do not make product decisions; record them as questions for the product owner.
- In `work/<id>-review.md`: what you found, what you fixed (files), which tests you added, what is left.
