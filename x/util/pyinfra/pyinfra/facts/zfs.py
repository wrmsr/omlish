"""
Manage ZFS filesystems.
"""

from pyinfra.api import FactBase, ShortFactBase


def _process_zfs_props_table(output):
    datasets: dict = {}
    for line in output:
        dataset, property, value, source = tuple(line.split("\t"))
        if dataset not in datasets:
            datasets[dataset] = {}
        datasets[dataset][property] = value
    return datasets


class Pools(FactBase):
    def command(self):
        return "zpool get -H all"

    @staticmethod
    def process(output):
        return _process_zfs_props_table(output)


class Datasets(FactBase):
    def command(self):
        return "zfs get -H all"

    @staticmethod
    def process(output):
        return _process_zfs_props_table(output)


class Filesystems(ShortFactBase):
    fact = Datasets

    @staticmethod
    def process_data(data):
        return {name: props for name, props in data.items() if props.get("type") == "filesystem"}


class Snapshots(ShortFactBase):
    fact = Datasets

    @staticmethod
    def process_data(data):
        return {name: props for name, props in data.items() if props.get("type") == "snapshot"}


class Volumes(ShortFactBase):
    fact = Datasets

    @staticmethod
    def process_data(data):
        return {name: props for name, props in data.items() if props.get("type") == "volume"}
