"""
god is it just easier to use qemu lol
https://ubuntu.com/server/docs/boot-arm64-virtual-machines-on-qemu
https://cloud-images.ubuntu.com/releases/22.04/release-20240726/
https://askubuntu.com/questions/451673/default-username-password-for-ubuntu-cloud-image

https://stackoverflow.com/questions/36617368/docker-centos-7-with-systemctl-failed-to-mount-tmpfs-cgroup
https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container#the_quest

https://hub.docker.com/r/centos/systemd/ old and dead
https://hub.docker.com/r/rockylinux/rockylinux
https://hub.docker.com/r/jrei/systemd-ubuntu

==

apt install \
    qemu-system \
    qemu-system-arm \
    qemu-efi \
    \
    guestfs-tools \
    libguestfs-tools \
    \
    linux-image-generic \

wget https://cloud-images.ubuntu.com/releases/22.04/release-20240726/ubuntu-22.04-server-cloudimg-arm64.img

LIBGUESTFS_BACKEND=direct virt-customize -a ubuntu-22.04-server-cloudimg-arm64.img --root-password password:barf

qemu-img convert -O qcow2 ubuntu-22.04-server-cloudimg-arm64.img ubuntu-22.04-server-cloudimg-arm64.qcow2

qemu-system-aarch64 \
    -M virt \
    -cpu cortex-a72 \
    -nographic \
    -net nic \
    -net user,hostfwd=tcp::10022-:22 \
    -bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd \
    -m 4G \
    -hda ubuntu-22.04-server-cloudimg-arm64.qcow2 \

==

https://gist.github.com/si458/98aa940837784e9ef9bff9e24a7a8bfd
"""
import os.path

from .. import utils as u


TIMEBOMB_DELAY_S = 20 * 60


def _main():
    img_name = 'wrmsr/omlish-sd-demo'
    cur_dir = os.path.dirname(__file__)
    u.build_docker_image(img_name, cur_dir)

    with u.launch_docker_container(img_name, timebomb_delay_s=TIMEBOMB_DELAY_S) as ctr_id:  # noqa
        pass


if __name__ == '__main__':
    _main()
