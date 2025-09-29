# Disable GPG checks for repositories (if needed)
sed -i 's/gpgcheck=1/gpgcheck=0/g' /etc/yum.repos.d/*.repo

# Install essential packages
dnf install -y \
    epel-release \
    vim \
    wget \
    git \
    tar \
    unzip \
    && dnf clean all

dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cmake \
    autoconf \
    automake \
    libtool \
    flex \
    bison \
    python3 \
    python3-pip \
    tbb \
    yum-utils \
    glibc-locale-source \
    glibc-langpack-en \
    tree \
    procps \
    perl \
    gperf \
    openssl-devel \
    tcl \
    tk \
    tk-devel \
    zlib-devel \
    readline-devel \
	ccache \
	boost-devel \
	boost-static \
    && dnf clean all

#yum install -y https://dl.fedoraproject.org/pub/epel/8/Modular/x86_64/Packages/s/swig-4.0.2-9.module_el8+12710+6335019d.x86_64.rpm
#yum install -y https://mirror.stream.centos.org/9-stream/AppStream/x86_64/os/Packages/boost-test-1.75.0-6.el9.x86_64.rpm
localedef -i en_US -f UTF-8 en_US.UTF-8

python3 -m pip install -r requirements.txt

# TODO: Enable to go back to home directory
mkdir -p /tmp/iverilog \
    && cd /tmp/iverilog \
    && git clone https://github.com/steveicarus/iverilog.git \
    && cd iverilog \
    && sh autoconf.sh \
    && ./configure &&  make && make install \
