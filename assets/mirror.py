#! /usr/bin/python

import os
import subprocess
import argparse
from datetime import datetime

mirror_bionic = {
    "UPSTREAM_URL": "http://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "REPO": "ubuntu",
    "OS_RELEASE": "bionic",
    "DISTS": ["bionic", "bionic-updates", "bionic-security", "bionic-backports"],
    "COMPONENTS": ["main", "restricted", "universe", "multiverse"],
    "ARCH": "amd64",
}

mirror_focal = {
    "UPSTREAM_URL": "http://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "REPO": "ubuntu",
    "OS_RELEASE": "focal",
    "DISTS": ["focal", "focal-updates", "focal-security", "focal-backports"],
    "COMPONENTS": ["main", "restricted", "universe", "multiverse"],
    "ARCH": "amd64",
}

mirror_bionic_arm = {
    "UPSTREAM_URL": "http://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "REPO": "ubuntu-ports",
    "OS_RELEASE": "bionic",
    "DISTS": ["bionic", "bionic-updates", "bionic-security", "bionic-backports"],
    "COMPONENTS": ["main", "restricted", "universe", "multiverse"],
    "ARCH": "arm64",
}

mirror_focal_arm = {
    "UPSTREAM_URL": "http://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "REPO": "ubuntu-ports",
    "OS_RELEASE": "focal",
    "DISTS": ["focal", "focal-updates", "focal-security", "focal-backports"],
    "COMPONENTS": ["main", "restricted", "universe", "multiverse"],
    "ARCH": "arm64",
}

mirror_list = {
    "ubuntu-bionic": mirror_bionic,
    "ubuntu-focal": mirror_focal,
    "ubuntu-bionic-arm": mirror_bionic_arm,
    "ubuntu-focal-arm": mirror_focal_arm,
}


def create(mirror):
    for dist in mirror["DISTS"]:
        os.system(
            "aptly mirror create -architectures=%s %s-%s %s %s %s"
            % (
                mirror["ARCH"],
                mirror["REPO"],
                dist,
                mirror["UPSTREAM_URL"],
                dist,
                " ".join(mirror["COMPONENTS"]),
            )
        )


def update(mirror):
    for dist in mirror["DISTS"]:
        os.system("aptly mirror update %s-%s" % (mirror["REPO"], dist))


def snapshot(mirror):
    today = datetime.now().strftime("%Y-%m-%d")
    snap_list = []
    # create snapshots
    for dist in mirror["DISTS"]:
        mirror_name = "%s-%s" % (mirror["REPO"], dist)
        snap_name = "%s-%s" % (mirror_name, today)
        os.system("aptly snapshot create %s from mirror %s" % (snap_name, mirror_name))
        snap_list.append(snap_name)
    # merge
    snap_merged = "%s-%s-merged-%s" % (mirror["REPO"], mirror["OS_RELEASE"], today)
    os.system("aptly snapshot drop %s" % (snap_merged))
    os.system("aptly snapshot merge -latest %s %s" % (snap_merged, " ".join(snap_list)))


def publish(mirror):
    today = datetime.now().strftime("%Y-%m-%d")
    snap_list = []
    # merge
    snap_merged = "%s-%s-merged-%s" % (mirror["REPO"], mirror["OS_RELEASE"], today)
    os.system(
        "aptly publish snapshot -batch -passphrase=Plusai2023 -distribution=%s %s %s"
        % (",".join(mirror["DISTS"]), snap_merged, mirror["REPO"])
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mirror",
        default="all",
        nargs="?",
        choices=["all", "ubuntu-bionic", "ubuntu-focal"],
    )
    parser.add_argument(
        "action",
        default="all",
        nargs="?",
        choices=["all", "create", "update", "snapshot", "publish"],
    )
    args = parser.parse_args()
    if args.mirror != "all":
        if args.action == "create":
            create(mirror_list[args.mirror])
        elif args.action == "update":
            update(mirror_list[args.mirror])
        elif args.action == "snapshot":
            snapshot(mirror_list[args.mirror])
        elif args.action == "publish":
            publish(mirror_list[args.mirror])


if __name__ == "__main__":
    main()
