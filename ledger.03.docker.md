
# Programming Ledger #4 - Building `ledger-app-btc` in Docker

[Docker](https://en.wikipedia.org/wiki/Docker_(software)) _is a set of platform as a service (PaaS) products that uses OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels. All containers are run by a single operating system kernel and therefore use fewer resources than virtual machines._ 

Building `ledger-app-btc` in docker lets you set up all of the parameters of the build in advance, which facilitates reproducibility and sharing, and enables you to run the build on environments other than Linux.

This document outlines an approach for building `ledger-app-btc` in docker.  Here is an overview of the process:

- Build a Docker image comprising the `BOLOS` development environment.
- Run the container. This builds the binary and copies it to the host computer.
- From the host computer, deploy the binary to a hardware wallet.

## Docker and Secrets

Secrets stored in a Docker image are not secure.  So if your build includes secrets - for example, passwords or tokens required to access github - you should be sure not to include them in the image.  The approach outlined here separates the build into two steps, 1) creating the image and 2) running the container.  Any sensitive steps should be deferred to the second step.

Regarding the problem that secrets in a Docker image are not secure, a workaround is to use Docker Swarm, which supports secure Secrets Management. Swarm is intended for a cluster of containers. Using Swarm for a single container solely to get access to Secrets Management seems like overkill and the approach is not adopted here.

## Build

Create a directory for your work:

    mkdir docker
    cd docker

Copy files [Dockerfile](examples.03/Dockerfile) and [build.sh](examples.03/build.sh) into your directory, and build the image:

    docker build -t erik/ledger:latest .

Once the build completes, the image should appear in your list:

```bash
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
erik/ledger         latest              96963e2d8493        3 days ago          3.19GB
```

The image includes the `BOLOS` development environment, including the SDK and `blue-loader-python`.

## Run

Create a `mount` directory:

    mkdir mount

The container will mount this directory and copy the build artifacts to it.

Run the container:

    docker run --name bld -v $PWD/mount:/mount -d erik/ledger:latest

After execution completes, check the log to make sure there were no errors:

    docker logs bld -f

The container builds the binary and other artifacts, and copies them to the mount directory. After the container exits, there might be a slight delay before the files appear:

```bash
$ ls -l mount
total 656
-rw-r--r-- 1 root root  82715 Apr 20 17:22 app.apdu
-rwxr-xr-x 1 root root 525048 Apr 20 17:22 app.elf
-rw-r--r-- 1 root root 111291 Apr 20 17:22 app.hex
-rw-r--r-- 1 root root     65 Apr 20 17:22 app.sha256
```

Before you can rerun the container, you need to delete the old one:

    docker container prune

That's it, the build is complete.  This example did not include any secrets.  But suppose that you have forked the `ledger-app-btc` repo into your own github repo which is protected by a password or token.  To handle that case, you would first uncomment the relevant lines from the `build.sh` script, and rebuild the image.  Then you would run the container like so:

```bash
export GIT_USERNAME=your_github_username
export GIT_TOKEN=your_github_token
docker run --name bld -v $PWD/mount:/mount -d erik/ledger:latest $GIT_USERNAME $GIT_TOKEN
```

## Install

Now we're done with docker.  The last step is to install the binary to your ledger.  For this you will need a python virtual environment containing `blue-loader-python` and `btchip-python` so let's create that:

```bash
mkdir repos
cd repos
git clone https://github.com/LedgerHQ/blue-loader-python.git
git clone https://github.com/LedgerHQ/btchip-python.git
python3 -m venv venv
source venv/bin/activate
pip3 install ./blue-loader-python
pip3 install ./btchip-python
deactivate
cd ..
```

Now download the script [load.sh](examples.03/load.sh).  Connect your ledger and run the script:

```bash
$ ./load.sh 
Generated random root public key : b'04fe257fff526064736f4152272d7ffaf3e4b193b3bfdb7f68a7d9ede7e3175c3267d35ed4a03f4f5e814b8fb51e86a0fd291d5eaaae803bfc24c551588aa4939e'
Using test master key b'04fe257fff526064736f4152272d7ffaf3e4b193b3bfdb7f68a7d9ede7e3175c3267d35ed4a03f4f5e814b8fb51e86a0fd291d5eaaae803bfc24c551588aa4939e' 
Using ephemeral key b'044029bc3640440b31b3642c7d3388da09d5ba5f40cbe2871a455df90d566f2717412c87d9aa1813ddd823780298006d29c96b5192c95fea88a1e3367b630fc7db'
Broken certificate chain - loading from user key
Application full hash : f09913f046ff52301bdec76d06d11cdc3974297d26f2446e3e9683505aedcb43
```
Voilà, you have deployed the app.
