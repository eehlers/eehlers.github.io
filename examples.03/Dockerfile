FROM ubuntu:bionic-20200311
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc-multilib \
    git \
    g++-multilib \
    libudev-dev \
    libusb-1.0-0.dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    tar \
    vim

WORKDIR /build/bolos-devenv
ADD https://launchpad.net/gcc-arm-embedded/5.0/5-2016-q1-update/+download/gcc-arm-none-eabi-5_3-2016q1-20160330-linux.tar.bz2 .
RUN tar xjvf gcc-arm-none-eabi-5_3-2016q1-20160330-linux.tar.bz2

ADD https://releases.llvm.org/7.0.0/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz .
RUN tar xvf clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz
RUN ln -s clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04 clang-arm-fropi

WORKDIR /build
RUN git clone https://github.com/LedgerHQ/nanos-secure-sdk
RUN git clone -b checksig https://github.com/btchip/blue-loader-python
RUN pip3 install ./blue-loader-python

ENV BOLOS_ENV="/build/bolos-devenv"
ENV BOLOS_SDK="/build/nanos-secure-sdk"

COPY ./build.sh /
RUN chmod +x /build.sh
ENTRYPOINT ["/build.sh"]

