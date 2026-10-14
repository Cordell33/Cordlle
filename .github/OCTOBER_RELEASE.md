# October 2026 release

The approved puzzle is stored in `.github/scripts/october_release.py`. The live
`index.html` stays unchanged until the scheduled release.

The workflow must be present on the GitHub default branch, `main`, before the
release. GitHub Actions must be enabled. GitHub Pages must use **Deploy from a
branch**, **main**, **/ (root)**. Branch rules must permit the workflow's normal
push to `main`; it never force-pushes.

The target is **October 15, 2026, 12:00 a.m. America/New_York (EDT)**, which is
**04:00 UTC**. The first job is scheduled for 03:50 UTC and waits until 04:00.
Safe retries are scheduled for 04:05, 04:15 and 04:30. GitHub can delay scheduled
runs, and Pages deployment takes additional time; exact midnight visibility is
not guaranteed. The script will not release before midnight or after October 15
Eastern time, including in later years.

Installing the workflow triggers a setup check and rebuilds the current game
without changing its puzzle. Before release, verify that this check is green in
the repository's **Actions** tab. It validates the puzzle, checks the Pages
source, and verifies the workflow can request and complete a Pages build.

At release, the workflow updates only the two puzzle arrays, commits and pushes
`index.html`, explicitly requests a Pages build, and verifies the published
commit. It refuses to overwrite puzzle data changed since preparation. Repeated
runs are safe and do not create duplicate release commits.

For a manual retry on October 15, open **Actions → October 2026 puzzle release →
Run workflow**, select **main**, and choose **release**. Choosing **check** at any
time validates setup and rebuilds the current page without releasing the puzzle.

For a local preview without changing the live game:

```sh
cd /workspace/Cordlle
python3 .github/scripts/october_release.py check --output /tmp/cordlle-october.html
```

To cancel before release, disable this workflow in GitHub Actions.
