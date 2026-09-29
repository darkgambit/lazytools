# -*- coding: utf-8 -*-
"""Stage a clean deploy directory, then publish it to Cloudflare Pages.

    python _generator/deploy.py                # build, stage, deploy
    python _generator/deploy.py --stage-only   # build and stage, do not upload
    python _generator/deploy.py --no-build     # reuse the existing staged tree

WHY THIS EXISTS
---------------
wrangler's Pages uploader does not read .gitignore or .assetsignore. Its entire filter
is a hardcoded nine-pattern list:

    _worker.js, _redirects, _headers, _routes.json, functions,
    **/.DS_Store, **/node_modules, **/.git, .wrangler

Every other file under the directory you point it at is uploaded and served. So
`wrangler pages deploy .` from this repo published INFO.md (real name, personal email,
country, GitHub handle), PROGRESS.md, CLAUDE-CODE-PROMPT.md, LAUNCH.md, _tests/,
_generator/ and .workbuddy-ai/ — all of which answered 200 on the live site.

The only lever is what is in the directory when wrangler walks it, so this script
assembles a directory holding nothing but publishable files, and deploys that.

Local preview must serve the same staged tree, or the emulator is not representative:
    npx wrangler@4 pages dev .wrangler/deploy --port 8788 --ip 127.0.0.1
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

STAGE = os.path.join(build.ROOT, ".wrangler", "deploy")
PROJECT = "lazytools"
BRANCH = "main"

# Top-level names that must never appear in a staged tree. Staging is built from a
# whitelist, so this can only fire if someone widens PUBLIC_DIRS/PUBLIC_FILES by mistake —
# which is exactly the mistake worth failing the deploy over.
PRIVATE = ["INFO.md", "PROGRESS.md", "LAUNCH.md", "README.md", "CLAUDE-CODE-PROMPT.md",
           ".gitignore", ".workbuddy-ai", "_generator", "_tests", ".wrangler", ".git"]


def _put(src, rel):
    """Copy one file from the repo into the staged tree at `rel`."""
    dst = os.path.join(STAGE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def stage():
    """Rebuild the staged tree so it is EXACTLY the publish whitelist — never a superset.

    Deliberately does not call shutil.rmtree. This environment shims recursive delete
    through the OS trash, and that shim failed on this very directory mid-session
    (`[safe-delete] trash-failed`), which took the whole build down. Removing the staged
    tree is not the hard part and must not be the fragile part, so files are written over
    the top and stale ones are unlinked one at a time.
    """
    wrote = build.main()
    os.makedirs(STAGE, exist_ok=True)

    wanted = set()

    for rel in wrote:
        _put(os.path.join(build.ROOT, rel.replace("/", os.sep)), rel)
        wanted.add(rel)

    for d in build.PUBLIC_DIRS:
        for dirpath, _, filenames in os.walk(os.path.join(build.ROOT, d)):
            for name in filenames:
                src = os.path.join(dirpath, name)
                rel = os.path.relpath(src, build.ROOT).replace(os.sep, "/")
                _put(src, rel)
                wanted.add(rel)

    for f in build.PUBLIC_FILES:
        _put(os.path.join(build.ROOT, f), f)
        wanted.add(f)

    # Drop anything left from an earlier stage, so a file that has since been removed from
    # the whitelist does not linger in the published tree.
    #
    # Note there is deliberately NO `os.rmdir` tidy-up of now-empty directories. In this
    # environment os.rmdir is shimmed to delete RECURSIVELY — probed directly: rmdir on a
    # directory containing a file reported success and removed the file too. A cosmetic
    # tidy-up loop therefore deleted `tools/` and `assets/` from the staged tree, which
    # would have deployed a site with no CSS, no JS and no tool pages while still printing
    # "Staged 35 files". Leaving an empty directory behind is harmless; removing it is not.
    stale = []
    for dirpath, _, filenames in os.walk(STAGE, topdown=False):
        for name in filenames:
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, STAGE).replace(os.sep, "/")
            if rel not in wanted:
                os.remove(p)
                stale.append(rel)
    if stale:
        print("Removed %d stale file(s) from the staged tree" % len(stale))

    # The guard that makes the whitelist trustworthy: if someone widens PUBLIC_DIRS or
    # PUBLIC_FILES by mistake, the deploy stops here instead of publishing personal data.
    leaked = sorted(p for p in wanted if p.split("/")[0] in PRIVATE or p in PRIVATE)
    if leaked:
        raise SystemExit("REFUSING TO DEPLOY — non-public files staged:\n  " +
                         "\n  ".join(leaked))

    # ...and the mirror-image guard: a staging bug that silently drops part of the site
    # would deploy a broken site that still reports success. Assert the tree on DISK, not
    # the whitelist in memory — that is the whole point, since the whitelist is what lied.
    expected = ["index.html", "404.html", "robots.txt", "sitemap.xml", "ads.txt", "_headers",
                "assets/style.css", "assets/app.js", "assets/ads.js",
                build.INDEXNOW_KEY + ".txt"]
    missing = [p for p in expected
               if not os.path.isfile(os.path.join(STAGE, p.replace("/", os.sep)))]
    tool_pages = [f for f in os.listdir(os.path.join(STAGE, "tools"))
                  if f.endswith(".html")] if os.path.isdir(os.path.join(STAGE, "tools")) else []
    if missing or len(tool_pages) != len(build.TOOLS):
        raise SystemExit("REFUSING TO DEPLOY — staged tree is incomplete:\n"
                         "  missing: %s\n  tool pages: %d (expected %d)"
                         % (", ".join(missing) or "none", len(tool_pages), len(build.TOOLS)))

    print("Staged %d files in %s" % (len(wanted), STAGE))
    return STAGE


def main():
    args = sys.argv[1:]
    if "--no-build" not in args:
        stage()
    elif not os.path.isdir(STAGE):
        raise SystemExit("no staged tree at %s — run without --no-build first" % STAGE)

    if "--stage-only" in args:
        print("--stage-only: not uploading.")
        return

    # Point wrangler at the STAGED directory, never at the repo root.
    cmd = 'npx --yes wrangler@4 pages deploy "%s" --project-name %s --branch %s' % (
        STAGE, PROJECT, BRANCH)
    print("$ " + cmd)
    subprocess.run(cmd, shell=True, check=True)

    print("\nDeployed. Now prove the private paths really are gone (cache-busted):")
    print("  python _tests/check_deploy.py %s" % build.SITE_URL)


if __name__ == "__main__":
    main()
