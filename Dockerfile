# =============================================================================
# Multi-stage Dockerfile
# OpenFOAM v2512 + preCICE v3.3.1 + OF-preCICE adapter v1.3.1 + solids4foam
# Target: Apple Silicon (M-series) via Rosetta 2 (linux/amd64)
#
# Build:  docker compose build
# Run:    docker compose run --rm fsi
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — compile preCICE, adapter, solids4foam
# ---------------------------------------------------------------------------
FROM --platform=linux/amd64 ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# OpenFOAM v2512 apt repository
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates wget gnupg && \
    wget -q -O - https://dl.openfoam.com/add-debian-repo.sh | bash && \
    apt-get update

# OpenFOAM + all build dependencies
RUN apt-get install -y --no-install-recommends \
      openfoam2512-default \
      build-essential cmake git pkg-config \
      libeigen3-dev libxml2-dev libboost-all-dev \
      python3-dev python3-numpy && \
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
# Using master — replace with --branch v2.3 if the tag exists on GitHub
RUN git clone --depth 1 https://github.com/solids4foam/solids4foam.git .
RUN source /usr/lib/openfoam/openfoam2512/etc/bashrc && \
    export S4F_NO_FILE_FIXES=1 && \
    ./Allwmake -j"$(nproc)" 2>&1 | tee /tmp/log.s4f

# ---------- Stage compiled artifacts into /opt for clean COPY ----------
RUN source /usr/lib/openfoam/openfoam2512/etc/bashrc && \
    mkdir -p /opt/of-user/{lib,bin} /opt/s4f-tutorials && \
    # Adapter + solids4foam shared libs
    cp -a ${FOAM_USER_LIBBIN}/*.so /opt/of-user/lib/ 2>/dev/null || true && \
    # solids4foam binaries (solids4Foam solver, utilities)
    cp -a ${FOAM_USER_APPBIN}/*   /opt/of-user/bin/  2>/dev/null || true && \
    # Tutorials for reference
    cp -a /build/s4f/tutorials/*  /opt/s4f-tutorials/ 2>/dev/null || true


# ---------------------------------------------------------------------------
# Stage 2: Runtime — lean image without build tools
# ---------------------------------------------------------------------------
FROM --platform=linux/amd64 ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# OpenFOAM v2512 runtime (pulls in MPI, Boost, etc. as deps)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates wget gnupg && \
    wget -q -O - https://dl.openfoam.com/add-debian-repo.sh | bash && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      openfoam2512-default \
      python3 python3-pip \
      python3-numpy python3-scipy python3-matplotlib \
      vim-tiny less && \
    rm -rf /var/lib/apt/lists/*

# preCICE libraries + headers + binaries
COPY --from=builder /opt/precice /opt/precice
RUN echo "/opt/precice/lib" > /etc/ld.so.conf.d/precice.conf && ldconfig

# Adapter + solids4foam compiled artifacts
COPY --from=builder /opt/of-user /opt/of-user
COPY --from=builder /opt/s4f-tutorials /opt/s4f-tutorials

# Auto-source OpenFOAM + custom paths on every shell (login + interactive)
RUN printf '#!/bin/bash\nsource /usr/lib/openfoam/openfoam2512/etc/bashrc\nexport PATH="/opt/precice/bin:/opt/of-user/bin:${PATH}"\nexport LD_LIBRARY_PATH="/opt/precice/lib:/opt/of-user/lib:${LD_LIBRARY_PATH}"\nexport PKG_CONFIG_PATH="/opt/precice/lib/pkgconfig:${PKG_CONFIG_PATH}"\n' \
      > /etc/profile.d/openfoam-fsi.sh && \
    chmod +x /etc/profile.d/openfoam-fsi.sh && \
    echo "source /etc/profile.d/openfoam-fsi.sh" >> /etc/bash.bashrc

# Simulation workspace — mount your case here
RUN mkdir -p /simulation
WORKDIR /simulation

CMD ["/bin/bash"]
