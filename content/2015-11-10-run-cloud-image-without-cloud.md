Title: Run cloud image without cloud
Category: Tech
Tags: libvirt; cloud-init; config drive; qcow2
Summary: How to run Linux Openstack image (Qcow2) on your machine without having any Openstack installed.
    The trick is to use *config drive* to inject ssh keys into VM.

[TOC]

## For the impatient

Modern cloud images have `cloud-init` pre-installed. You can feed cloud-init bootstrap
information via iso image attached as cdrom device, so called *config drive*.
There, you can store 1) meta-data as if they were provided by cloud, 2) user-data as if they were
specified on VM creation.

For the minimal setup, you only need the meta-data with the public key.
Here is how the iso content should look like:

    .
    └── openstack
        └── latest
            └── meta_data.json

Where `meta_data.json` looks like:

    :::json
    {
        "public_keys": {
            "<arbitrary-key-name>": "ssh-rsa <public-key>\n"
        },
        "uuid": "<any-uuid-value>"
    }

At boot time, public key is injected into cloud user's `authorized_keys` file (eg. "centos" user for CentOS cloud image).

## Motivation

Installing VM from installation media ? Hell, no!
At least not if you intend to drop & re-create your VM repeatedly.
You have DHCP/PXE/Kickstart to automate it, you know..
Well, ok, but not if you need something working.. like now.

Vagrant ?
Weeeell, maybe the config written in Ruby is not your thing.
Or the image you want to run is not public and you have only Qcow2 version and no Vagrant.

Or simply, you don't intend to test software on your VM, rather deployment automation (Ansible, Puppet, ..)
In which case, you probably want to test it on exactly the same image as in the cloud.

(Or you just want to do it by hand for the sake of it)

## Before You Begin

**Problem**: Openstack images have no default root password or password-less account.
You *can* run the image as-is, but you won't be able to login.
That's where *config drive* comes in.
Simply put, it's an iso image attached as cdrom to the VM.

I did enhance this guide a bit to allow *sharing* of the same base image by several instances.
This step is completely optional.
It won't affect the config drive if you skip it.

I'll be using Fedora as host, but you should be able to adapt the examples easily to your distro.

It does not matter what image you want to run in the guest VM as long as
it has cloud-init pre-installed.

## Preparation

### Install qemu/libvirt

    :::bash
    # install packages from "virtualization" group
    sudo dnf install @virtualization -y

    # start libvirtd
    sudo systemctl start libvirtd

### Configure network

VM running in the cloud receives IP address and hostname from the cloud provider via DHCP.
In your libvirt setup, VM would get a random IP from the pool and NO hostname.
Let's fix that first..

    :::bash
    # edit 'default' network and add static DHCP
    sudo virsh net-edit default

Snippet that should be added inside `<dhcp>` tag (I'm assuming that your default network
has the same range as mine - 192.168.122.0/24):

    :::xml
    <dhcp>
      ...
      <host mac='52:54:00:00:00:11' name='vm1' ip='192.168.122.11'/>
      <host mac='52:54:00:00:00:12' name='vm2' ip='192.168.122.12'/>
      <host mac='52:54:00:00:00:13' name='vm3' ip='192.168.122.13'/>
      <host mac='52:54:00:00:00:14' name='vm4' ip='192.168.122.14'/>
    </dhcp>

!!! note "Why static MAC ?"

    The MAC address will later be used when creating the VM.
    It is IMHO easier to *provide* MAC to VM, rather than *fetch* (randomly generated) MAC from VM.
    Also, you only need to define this mapping *once*, no matter how many VMs you intend
    to run.

Apply changes by restarting `dnsmasq`:

    :::bash
    sudo virsh net-destroy default
    sudo virsh net-start   default

(optional) You might want to add your VMs to `/etc/hosts` file:

    ...
    192.168.122.11  vm1
    192.168.122.12  vm2
    192.168.122.13  vm3
    192.168.122.14  vm4

### Configure storage

OK, now is the time to decide which image you want to run inside the guest.
Decent distros provide pre-built Qcow2 images ready to be imported to Openstack.
Here is a good source: ["Get images" in Openstack's doc].
Download one of them..

["Get images" in Openstack's doc]: http://docs.openstack.org/image-guide/content/ch_obtaining_images.html

I will go for CentOS for now..

    :::bash
    mkdir ~/virt
    cd ~/virt
    wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2.xz
    xz -d CentOS-7-x86_64-GenericCloud.qcow2.xz

Create copy-on-write storage for VMs with pristine CentOS as read-only backing-store:

    :::bash
    for VMID in 1 2 3 4; do
        qemu-img create -f qcow2 -o backing_file=CentOS-7-x86_64-GenericCloud.qcow2 vm${VMID}.qcow2
    done

!!! note "Qcow2 size"

    Note, I did not specify the device size.
    By default, VM will get 8GB of "sparse" storage.

In this example setup, all four VMs share the same base (CentOS) image.
Note that blank VM occupy only 200kB:

    :::bash
    $ du -shc CentOS-7-x86_64-GenericCloud.qcow2 vm?.qcow2
    959M    CentOS-7-x86_64-GenericCloud.qcow2
    196K    vm1.qcow2
    196K    vm2.qcow2
    196K    vm3.qcow2
    196K    vm4.qcow2
    960M    total

### Create minimal config drive

This is the *important* part.
Config drive is the way to pass information to the VM, "outside" of disk image.
We will create a *minimal* iso image that will inject just the ssh public key.
For the full documentation, refer to [Openstack's "Store metadata on a configuration drive"][].

[Openstack's "Store metadata on a configuration drive"]: http://docs.openstack.org/user-guide/cli_config_drive.html

The content of the ISO image (naturally, fill-in your public key):

    :::bash
    mkdir -p config-drive/openstack/latest
    cat >config-drive/openstack/latest/meta_data.json <<'EOF'
    {
        "public_keys": {
            "bza": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEA6rCBkwpHYS073jjOMEUrHAAtA7ovYgBv4FIdb+oD5Yn7UEffzp0fLxhJDkv9hqp3uYk6T/N++HUIeI8oFcfZ1gM00LB70Uv5IkCAy9SztvltOK781NQD1urU8i5j1l9cYLHhyYnGmM9McM77+ZY8IiPSl9jznnRquW7925UrO40= Brano Zarnovican\n"
        },
        "uuid": "83679162-1378-4288-a2d4-70e13ec132aa"
    }
    EOF

!!! warning "Valid json"
    Be careful to provide a valid json file.
    Otherwise, you might waste a lot of time on troubleshooting.

!!! note "What's that UUID for?"

    That is a mandatory field in Openstack meta_data.json.
    It's ok to have some hard-coded value for your local VM.
    It is even ok to share the same config drive (and UUID value) for all your VMs.

    Having just the "public_keys" and "uuid" field may be breaking some meta-data standard.
    It is working, though.

Create the ISO image:

    mkisofs -R -o config-drive.iso config-drive/

### Create VM

Time to tie it all together..

    :::bash
    VMID=1
    sudo virt-install --name vm${VMID} --memory 1024 --vcpus 1 --import \
        --disk vm${VMID}.qcow2,bus=virtio \
        --disk config-drive.iso,device=cdrom,perms=ro \
        --network network=default,model=virtio,mac=52:54:00:00:00:1${VMID} \
        --noautoconsole

!!! tip "virt-manager"

    Alternatively, you can create the VM using virt-manager.
    Just remember to:

    * import existing qcow2 image (vmX.qcow2)
    * change the MAC address on network interface to 52:54:00:00:00:1X
    * add IDE CDROM with config-drive.iso

## And we are done..

If all worked well, you should be able to login..

    :::
    $ ssh centos@vm1
    The authenticity of host 'vm1 (192.168.122.11)' can't be established.
    ECDSA key fingerprint is SHA256:JrczAJifE04hx+NUF4yTWVHA/6hh+XqELCViluVEW6Q.
    ECDSA key fingerprint is MD5:96:f0:85:88:53:3a:c5:47:c3:d2:3e:d8:a6:c1:c6:ff.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added 'vm1,192.168.122.11' (ECDSA) to the list of known hosts.
    [centos@vm1 ~]$
    [centos@vm1 ~]$ sudo -i
    [root@vm1 ~]#

### What is VM's base image ?

To query Qcow2 file..

    :::bash
    $ qemu-img info vm1.qcow2
    image: vm1.qcow2
    file format: qcow2
    virtual size: 8.0G (8589934592 bytes)
    disk size: 70M
    cluster_size: 65536
    backing file: CentOS-7-x86_64-GenericCloud.qcow2
    Format specific information:
        compat: 1.1
        lazy refcounts: false
        refcount bits: 16
        corrupt: false

### Re-image the VM

Throw away VM's data and start again from pristine image.

    :::bash
    VMID=1

    # stop the instance, ok to be "ungraceful" at this point
    sudo virsh destroy vm${VMID}

    # destroy and recreate its storage
    cd ~/virt
    rm -f vm${VMID}.qcow2
    qemu-img create -f qcow2 -o backing_file=CentOS-7-x86_64-GenericCloud.qcow2 vm${VMID}.qcow2

    # start the instance again
    sudo virsh start vm${VMID}

Note, that you don't need to undefine the whole VM.
Destroy or shutdown is enough.
VM will retain hw configuration, network MAC address, etc, but it will loose all data.
You can also switch to a different "base image" while VM is down.

### Troubleshooting cloud-init

This is tricky.
Something did not work, and now you are not able to login to the VM to have a look at things.
You can still mount the image on host OS and poke around (as root).

    :::bash
    # mount
    modprobe nbd max_part=63
    qemu-nbd -c /dev/nbd0 /home/user/virt/vm1.qcow2
    mount /dev/nbd0p1 /mnt/

    # umount
    umount /mnt
    qemu-nbd -d /dev/nbd0

Just make sure you don't have it mounted on host and guest at the same time..
Cloud-init log file will be in `/mnt/var/log/cloud-init.log`,
but you might need to first increase verbosity in `/mnt/etc/cloud/cloud.cfg.d/*logging.cfg`

## Extras

### Static host ssh key

It's quite annoying to update `known_hosts` file every time I re-image the VM.
One way to fix this is to "give" VM static host keys at first boot via cloud-init.
Its config is in cloud's "user data".

    :::bash
    cat >config-drive/openstack/latest/user_data <<'EOF'
    #cloud-config

    ssh_keys:
      rsa_private: |
        -----BEGIN RSA PRIVATE KEY-----
        MIIBxwIBAAJhAKD0YSHy73nUgysO13XsJmd4fHiFyQ+00R7VVu2iV9Qcon2LZS/x
        1cydPZ4pQpfjEha6WxZ6o8ci/Ea/w0n+0HGPwaxlEG2Z9inNtj3pgFrYcRztfECb
        1j6HCibZbAzYtwIBIwJgO8h72WjcmvcpZ8OvHSvTwAguO2TkR6mPgHsgSaKy6GJo
        PUJnaZRWuba/HX0KGyhz19nPzLpzG5f0fYahlMJAyc13FV7K6kMBPXTRR6FxgHEg
        L0MPC7cdqAwOVNcPY6A7AjEA1bNaIjOzFN2sfZX0j7OMhQuc4zP7r80zaGc5oy6W
        p58hRAncFKEvnEq2CeL3vtuZAjEAwNBHpbNsBYTRPCHM7rZuG/iBtwp8Rxhc9I5w
        ixvzMgi+HpGLWzUIBS+P/XhekIjPAjA285rVmEP+DR255Ls65QbgYhJmTzIXQ2T9
        luLvcmFBC6l35Uc4gTgg4ALsmXLn71MCMGMpSWspEvuGInayTCL+vEjmNBT+FAdO
        W7D4zCpI43jRS9U06JVOeSc9CDk2lwiA3wIwCTB/6uc8Cq85D9YqpM10FuHjKpnP
        REPPOyrAspdeOAV+6VKRavstea7+2DZmSUgE
        -----END RSA PRIVATE KEY-----

      rsa_public: ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEAoPRhIfLvedSDKw7XdewmZ3h8eIXJD7TRHtVW7aJX1ByifYtlL/HVzJ09nilCl+MSFrpbFnqjxyL8Rr/DSf7QcY/BrGUQbZn2Kc22PemAWthxHO18QJvWPocKJtlsDNi3 smoser@localhost

      ecdsa_private: |
        -----BEGIN EC PRIVATE KEY-----
        MHcCAQEEIIjH3F2tInhb1SpODeeis+7XZexdJQAjVCDUVkfQTjYyoAoGCCqGSM49
        AwEHoUQDQgAE9cHv9N9K4UF6GyGlHNR82ylKiv715LBZuXOyxezAL+FFiTMo6/qZ
        y+6rMEJYdkWxqXz4iKkiU/rgmCWvBfC1FQ==
        -----END EC PRIVATE KEY-----

      ecdsa_public: ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPXB7/TfSuFBehshpRzUfNspSor+9eSwWblzssXswC/hRYkzKOv6mcvuqzBCWHZFsal8+IipIlP64JglrwXwtRU=

    EOF

