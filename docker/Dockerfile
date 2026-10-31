# rf-tools: openroad/orfs:latest + iverilog + cocotb, used by ~/bin/rf.
# Rebuild:  docker build -t rf-tools \
#             --build-arg USERNAME=$(id -un) --build-arg UID=$(id -u) --build-arg GID=$(id -g) ~/regbus/docker
FROM openroad/orfs@sha256:ca289d6df8401711a4ed310a83b5bd14fd42534d64b9b790bf5cbb02cc496278

ARG USERNAME=aru
ARG UID=1000
ARG GID=1000

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends iverilog \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir cocotb==1.9.2 matplotlib==3.10.3 scipy==1.15.3

# Give the host uid/gid a name inside the container (no "I have no name!" prompt).
RUN (getent group "$GID" >/dev/null || groupadd -g "$GID" "$USERNAME") \
 && (getent passwd "$UID" >/dev/null || useradd -u "$UID" -g "$GID" -d "/home/$USERNAME" -M -s /bin/bash "$USERNAME")

# Tools on PATH without sourcing env.sh, and absolute tool paths for a host-side
# ~/OpenROAD-flow-scripts/flow (which has no tools/install of its own).
ENV PATH=/OpenROAD-flow-scripts/tools/install/OpenROAD/bin:/OpenROAD-flow-scripts/tools/install/yosys/bin:/OpenROAD-flow-scripts/tools/install/kepler-formal/bin:${PATH} \
    OPENROAD_EXE=/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad \
    YOSYS_EXE=/OpenROAD-flow-scripts/tools/install/yosys/bin/yosys \
    KLAYOUT_CMD=/usr/bin/klayout

# sby (SymbiYosys) for the formal stretch item, plus the z3 solver
ARG SBY_REF=v0.68
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git ca-certificates z3 \
 && rm -rf /var/lib/apt/lists/* \
 && git clone --depth 1 --branch ${SBY_REF} https://github.com/YosysHQ/sby /tmp/sby \
 && make -C /tmp/sby install PREFIX=/usr/local \
 && rm -rf /tmp/sby
