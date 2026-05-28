# =============================================================================
# Multi-stage Dockerfile
# OpenFOAM v2512 + preCICE v3.3.1 + OF-preCICE adapter v1.3.1 + solids4foam
# + CalculiX 2.20 + CalculiX-preCICE adapter v2.20.1
# Target: Apple Silicon (M-series) via Rosetta 2 (linux/amd64)
#
# Build:  docker compose build
# Run:    docker compose run --rm fsi
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — compile preCICE, adapter, solids4foam, CalculiX
# ---------------------------------------------------------------------------
FROM --platform=linux/amd64 public.ecr.aws/ubuntu/ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# OpenFOAM v2512 apt repository
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates wget gnupg && \
    wget -q -O - https://dl.openfoam.com/add-debian-repo.sh | bash && \
    apt-get update

# OpenFOAM + all build dependencies (includes CalculiX deps)
RUN apt-get install -y --no-install-recommends \
      openfoam2512-default \
      build-essential cmake git pkg-config \
      libeigen3-dev libxml2-dev libboost-all-dev \
      python3-dev python3-numpy \
      gfortran \
      libarpack2-dev libspooles-dev libyaml-cpp-dev \
      libblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]

# ---------- preCICE (from source, no arm64 .deb available) ----------
ARG PRECICE_VER=3.3.1
WORKDIR /build/precice
RUN git clone --branch v${PRECICE_VER} --depth 1 \
      https://github.com/precice/precice.git . && \
    cmake -B build \
      -DCMAKE_INSTALL_PREFIX=/opt/precice \
      -DCMAKE_BUILD_TYPE=Release \
      -DPRECICE_FEATURE_PETSC_MAPPING=OFF \
      -DPRECICE_FEATURE_PYTHON_ACTIONS=OFF \
      -DBUILD_TESTING=OFF && \
    cmake --build build -j"$(nproc)" && \
    cmake --install build

# ---------- OpenFOAM-preCICE adapter ----------
ARG ADAPTER_VER=1.3.1
WORKDIR /build/adapter
RUN git clone --branch v${ADAPTER_VER} --depth 1 \
      https://github.com/precice/openfoam-adapter.git .
RUN source /usr/lib/openfoam/openfoam2512/etc/bashrc && \
    export PKG_CONFIG_PATH="/opt/precice/lib/pkgconfig:${PKG_CONFIG_PATH}" && \
    export LD_LIBRARY_PATH="/opt/precice/lib:${LD_LIBRARY_PATH}" && \
    ./Allwmake -j"$(nproc)"

# ---------- solids4foam ----------
WORKDIR /build/s4f
RUN git clone --depth 1 https://github.com/solids4foam/solids4foam.git .
RUN source /usr/lib/openfoam/openfoam2512/etc/bashrc && \
    export S4F_NO_FILE_FIXES=1 && \
    ./Allwmake -j"$(nproc)" 2>&1 | tee /tmp/log.s4f

# ---------- Stage OpenFOAM compiled artifacts ----------
RUN source /usr/lib/openfoam/openfoam2512/etc/bashrc && \
    for d in src/solids4FoamModels src/blockCoupledSolids4FoamTools; do \
      if [ -d "/build/s4f/$d" ]; then \
        cd /build/s4f/$d && wmakeLnInclude -u . ; \
      fi ; \
    done && \
    mkdir -p /opt/of-user/lib /opt/of-user/bin /opt/of-user/src/solids4foam /opt/s4f-tutorials && \
    cp -a ${FOAM_USER_LIBBIN}/*.so /opt/of-user/lib/ 2>/dev/null || true && \
    cp -a ${FOAM_USER_APPBIN}/*   /opt/of-user/bin/  2>/dev/null || true && \
    cp -a /build/s4f/tutorials/*  /opt/s4f-tutorials/ 2>/dev/null || true && \
    cp -a /build/s4f/src          /opt/of-user/src/solids4foam/ 2>/dev/null || true

# ---------- CalculiX 2.20 source + preCICE adapter v2.20.1 ----------
ARG CCX_VER=2.20
ARG CCX_ADAPTER_VER=2.20.1

# Download and extract CalculiX source (creates /build/CalculiX/ccx_2.20/src)
WORKDIR /build
RUN wget -q https://www.dhondt.de/ccx_${CCX_VER}.src.tar.bz2 && \
    tar xjf ccx_${CCX_VER}.src.tar.bz2 && \
    rm ccx_${CCX_VER}.src.tar.bz2

# Build the CalculiX-preCICE adapter (produces ccx_preCICE binary)
WORKDIR /build/calculix-adapter
RUN git clone --branch v${CCX_ADAPTER_VER} --depth 1 \
      https://github.com/precice/calculix-adapter.git .
RUN export PKG_CONFIG_PATH="/opt/precice/lib/pkgconfig:${PKG_CONFIG_PATH}" && \
    export LD_LIBRARY_PATH="/opt/precice/lib:${LD_LIBRARY_PATH}" && \
    export HOME=/build && \
    # GCC 10+ workaround — add -fallow-argument-mismatch to any FFLAGS line
    sed -i 's|-fopenmp|-fopenmp -fallow-argument-mismatch|' Makefile && \
    make -j"$(nproc)"

# Stage CalculiX binary for clean COPY
RUN mkdir -p /opt/calculix/bin && \
    cp /build/calculix-adapter/bin/ccx_preCICE /opt/calculix/bin/


# ---------------------------------------------------------------------------
# Stage 2: Runtime — lean image without build tools
# ---------------------------------------------------------------------------
FROM --platform=linux/amd64 public.ecr.aws/ubuntu/ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# OpenFOAM v2512 runtime + CalculiX runtime deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates wget gnupg && \
    wget -q -O - https://dl.openfoam.com/add-debian-repo.sh | bash && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      openfoam2512-default \
      python3 python3-pip \
      python3-numpy python3-scipy python3-matplotlib \
      vim-tiny less \
      libarpack2-dev libspooles-dev libyaml-cpp-dev \
      libgfortran5 libblas3 liblapack3 && \
    rm -rf /var/lib/apt/lists/*

# preCICE libraries + headers + binaries
COPY --from=builder /opt/precice /opt/precice

# Boost runtime libs — copied from builder (avoids apt-get network dependency)
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_log.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_log_setup.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_filesystem.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_program_options.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_system.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_timer.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_chrono.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_atomic.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_thread.so* /usr/lib/x86_64-linux-gnu/

RUN echo "/opt/precice/lib" > /etc/ld.so.conf.d/precice.conf && ldconfig

# Adapter + solids4foam compiled artifacts
COPY --from=builder /opt/of-user /opt/of-user
COPY --from=builder /opt/s4f-tutorials /opt/s4f-tutorials

# CalculiX-preCICE binary
COPY --from=builder /opt/calculix /opt/calculix

# Auto-source OpenFOAM + custom paths on every shell (login + interactive)
RUN printf '#!/bin/bash\nsource /usr/lib/openfoam/openfoam2512/etc/bashrc\nexport PATH="/opt/precice/bin:/opt/of-user/bin:/opt/calculix/bin:${PATH}"\nexport LD_LIBRARY_PATH="/opt/precice/lib:/opt/of-user/lib:${LD_LIBRARY_PATH}"\nexport PKG_CONFIG_PATH="/opt/precice/lib/pkgconfig:${PKG_CONFIG_PATH}"\n' \
      > /etc/profile.d/openfoam-fsi.sh && \
    chmod +x /etc/profile.d/openfoam-fsi.sh && \
    echo "source /etc/profile.d/openfoam-fsi.sh" >> /etc/bash.bashrc

# Simulation workspace — mount your case here
RUN mkdir -p /simulation
WORKDIR /simulation

CMD ["/bin/bash"]
