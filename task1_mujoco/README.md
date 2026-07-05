> **Location note**: this directory (`task1_mujoco/`) is the MuJoCo
> implementation of Task 1 (cable management) inside the
> EBiM-Benchmark/benchmark repository, the sibling of `task1_isaacsim/`.
> It is self-contained: simulator, ManipulationNet client, teleop publisher
> packages, Docker stack and one-click scripts all live here. The
> `teleop_ros2/` packages are also proposed upstream to the
> `EBiM-Benchmark/teleoperation` repository (branch
> `2houyuhang/feature/mujoco-teleop-publishers`); once merged there, the
> copy here can be swapped for a submodule reference.

# EBiM Benchmark Task 1 — Cable Management Simulation

A MuJoCo teleoperation environment for the ManipulationNet **cable_management**
benchmark (Tier 2 board): a mobile dual-arm Franka FR3 platform with Robotiq
2F-85 grippers routes a deformable cable across a fixture board. The simulator
supports **keyboard, gamepad, VR, GELLO, and a unified ROS 2 teleop mode**
and integrates the
official ManipulationNet ROS 2 client for end-to-end evaluation — including a
fixed overhead evidence camera, automatic tier skipping, client-driven fixture
randomization, and an in-scene one-time-code display.

## Which path do I take?

All commands below run from this directory (`task1_mujoco/` after cloning
the benchmark repository — you already have everything, nothing else to
download).

| You want to... | Use | You need |
|---|---|---|
| **Drive the robot now** (keyboard / gamepad / VR), best performance and feel | **Path A — native**: `start.bat` (Windows) / `start.sh` (Ubuntu) | Miniconda (auto-installed by `start.sh`) |
| **Run the scored ManipulationNet evaluation** | **Path B — eval stack**: `./eval.sh` | Docker only |
| **Check the sim runs on your machine** without installing anything native | **Path C — Docker test**: `./docker-run.sh` | Docker only |
| Use **GELLO hardware** or feed commands **over ROS 2 topics** | Path B's image + the [GELLO](#gello-official-ebim-competition-input-device) / [ros_teleop](#unified-ros-2-teleop---input-ros_teleop) sections | ROS 2 (included in the eval image) |

The typical participant journey is: **practice with Path A, score with
Path B.** All paths run the same simulator and the same control stack — one
physics configuration, one in-sim IK, identical feel.

### Input modes at a glance

Every path launches the same entry point; pick the device with `--input`:

| `--input` | Device needed | ROS 2? | Verified so far |
|---|---|---|---|
| `keyboard` (default) | none | no | Windows + Ubuntu with real keyboards (Linux needs X11/XWayland — forced automatically under Wayland) |
| `gamepad` | any SDL-recognized pad (Xbox / PS / generic) | no | Windows with a real pad; Ubuntu pending (same SDL mapping, so the layout is identical) |
| `vr` | OpenXR headset (Quest 2/3, Index, Vive) | no | Windows via Quest Link; Ubuntu via WiVRn pending |
| `gello` | GELLO Duo hardware + the official publisher running | yes | topic contract with synthetic data; real hardware pending |
| `ros_teleop` | any teleop publisher node (keyboard/gamepad publishers included in `teleop_ros2/`) | yes | end-to-end with the publishers' synthetic self-test (`--pattern`); real-device runs pending |

"Pending" = implemented and passing automated / synthetic tests, but not yet
validated by us on that platform or hardware — those combinations are in
**community testing**. If you run one, a quick report (works / broken, plus
the terminal log) via GitHub Issues helps every team.

### Architecture

```
 OPERATOR SIDE                                      SIMULATOR (this dir, main.py)
 ─────────────                                      ─────────────────────────────
 local devices (no ROS)
   keyboard / gamepad / OpenXR headset ───────────► --input keyboard|gamepad|vr

 teleop publisher nodes (teleop_ros2/, or your own)
   keyboard_teleop_publisher ──┬── /cmd_vel
   gamepad_teleop_publisher  ──┤   /left|right/teleop_cmd ────► --input ros_teleop
                               └── /left|right/gripper_cmd
              ▲ /mujoco/teleop_feedback (camera azimuth + robot yaw, 30 Hz)

 official EBiM teleoperation repo (GELLO rig)
   franka_gello_state_publisher ── /left|right/gello/joint_states ─► --input gello
   pedal_state_publisher ───────── /pedal/state (drives the base) ─►

         every input lands in the same control stack: grasp-aware scaling →
         smoothing → contact clamp → damped-least-squares IK → force-servo
         grasping   (gello is the exception: joint-space 1:1, no IK)

 evaluation stack (Docker, ./eval.sh)
   official mnet client ◄── /mujoco/camera/image_raw   (fixed overhead camera)
                        ◄── F / H completion reports
                        ──► fixture randomization, one-time code
```

## Path A — native teleoperation

### Windows (keyboard / gamepad / VR)

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. Double-click **`start.bat`** — the first run creates the conda environment
   automatically (a few minutes), then the viewer opens. Later runs also
   self-check the environment and install anything missing.

```bat
start.bat                      :: keyboard
start.bat --input gamepad      :: gamepad
start.bat --input vr           :: VR (see VR setup below)
start.bat --no-viewer          :: headless self-check ("init/smoke ok")
```

### Ubuntu (keyboard / gamepad / VR)

```bash
cd task1_mujoco                # this directory, inside your benchmark clone
./start.sh                     # installs Miniconda if missing, creates the env
./start.sh --input gamepad
./start.sh --input vr          # see VR setup below
```

### VR setup

The VR code is pure OpenXR and works with any active runtime:

| Headset | Windows | Ubuntu |
|---|---|---|
| Quest 2/3 | Meta Quest Link (set as active OpenXR runtime) | [WiVRn](https://github.com/WiVRn/WiVRn) (no Steam) or ALVR + SteamVR |
| Index / Vive | SteamVR | SteamVR |

Wear the headset (or cover the proximity sensor) when starting — the runtime
reports the device unavailable otherwise. On Ubuntu an X11 session is
required (the launcher forces XWayland automatically under Wayland).

## Path B — ManipulationNet evaluation (Docker + ROS 2)

Everything ROS-related is containerized: you only install Docker. On Ubuntu
use Docker natively. On Windows, WSL2 + Docker Desktop runs the pipeline
logic, but its software rendering cannot reach the evidence camera's required
25 fps (the client refuses lower rates and the sim warns you after ~15 s) —
**scored runs need native Linux** (or a 3D-accelerated VM).

Step by step:

1. **Start the stack** — the first run builds the image from source
   (one-time, several minutes):

   ```bash
   xhost +local:docker   # native Linux, once per login session
   ./eval.sh sim         # terminal 1: simulator + eval bridge (viewer opens)
   ```

2. **Start the client** in a second terminal, pick `cable_management` →
   `local_test` in its menu:

   ```bash
   ./eval.sh client
   ```

   `mnet_client-ros_2/config/team_config.json` ships pre-filled for local
   testing (no registration needed). Replace `team_unique_code` with your
   real code only for an official `submission` run (attempts are
   rate-limited — see the [mnet docs](https://mnet-client.readthedocs.io/)).

3. **Session flow**: tiers other than Tier 2 are skipped automatically → on
   Tier 2 the board fixtures are randomized per the client's published
   coordinates and the cable is re-laid → when the client shows the one-time
   code, type `code <TEXT>` into the **simulator** terminal (it appears on
   the plate next to the board, inside the evidence camera frame) → route
   the cable → press `F` in the viewer to report completion → remaining
   tiers auto-skip and the client finishes on its own.

4. **Results**: videos and logs land in
   `robotiq_duo_full_scene_minimal_core/release/mnet_out/`. Scoring uses the
   fixed ceiling evidence camera above the board, not your viewer.

5. Done: `./eval.sh down`.

## Path C — cross-platform Docker test (no ROS)

For verifying the sim behaves identically on Windows and Linux without
installing conda/mujoco natively (a smaller, ROS-free image; see
[RELEASE.md](robotiq_duo_full_scene_minimal_core/RELEASE.md) for how it
compares to the eval image):

```bash
./docker-run.sh                    # keyboard (default)
./docker-run.sh --input gamepad    # gamepad (native Linux only, see below)
./docker-run.sh --no-viewer       # headless self-check
./docker-run.sh build              # rebuild the image only
```

Two things cannot work inside any container, by nature of what they need:

- **Gamepad** needs `/dev/input` passthrough, only available on native Linux
  Docker (not WSL2) — uncomment the `devices:` line for the `runtime`
  service in `robotiq_duo_full_scene_minimal_core/release/compose.yaml`.
- **VR** needs direct host device/driver access — use Path A for VR.

Native Linux needs `xhost +local:docker` once per session, same as Path B.

## Prebuilt image (planned — not published yet)

Paths B and C currently **build** the Docker image from this directory (that
is why you clone the repository first). Once the image is published to a
container registry, cloning becomes optional: you will be able to
`docker compose pull` a ready image using only `release/compose.dist.yaml`
in an empty folder. Until that registry location is announced,
`docker compose pull` has nothing to pull — use Paths B/C above, which build
automatically.

## Controls

**Keyboard** (motion uses the arrow-key cluster; letters stay free):
`7/8/9` select base / left arm / right arm ·
base mode: arrows drive in **screen directions**, `Home`/`End` turn,
`PageUp`/`PageDown` move the spine ·
arm modes: arrows translate, `PageUp`/`PageDown` for Z, `R` toggles rotation
(arrows = yaw/pitch, `PageUp`/`PageDown` = roll) ·
`G` close gripper (force servo) · `V`/`Space` open · `-`/`=` speed ·
`F`/`H` report task finished / skipped (eval mode)

**Gamepad** (identical layout on every OS via SDL's controller mapping):
`Share` base · `L1`/`R1` arms · left stick translate ·
right stick turn / orient · `L2`/`R2` vertical · `○/B` close · `×/A` open ·
click left/right stick = speed up/down · one rumble pulse on new contact

**VR** (mirror teleop, operator faces the screen): hold **grip** to drive the
corresponding arm, release to lock · **trigger** close, `A/X` open ·
right stick base translation, left stick turn/spine ·
**click left/right stick = speed up/down** · one haptic pulse on new contact ·
monitor view by default, `--hmd-view` for an in-headset screen

**GELLO**: move the physical GELLO Duo arms — sim arms follow 1:1 in joint
space (no clutch, no IK: GELLO already gives absolute joint angles) ·
squeeze the GELLO gripper to grasp (same force-servo physics as every other
input mode) · keyboard drives the mobile base (arrows/`Home`/`End`/
`PageUp`/`PageDown`, same as keyboard mode)

## GELLO (official EBiM competition input device)

`--input gello` subscribes to the ROS 2 topics published by the official
[`franka_gello_state_publisher`](https://github.com/EBiM-Benchmark/teleoperation)
— it does not talk to the Dynamixel/OpenRB-150 hardware directly, so that
reference node (with its calibrated `assembly_offsets`/`joint_signs`/gripper
range per your physical rig) must already be running and publishing on
`/left` and `/right`. This needs ROS 2 (rclpy), same as `--mnet` — run it
inside the eval Docker image or a native ROS 2 / RoboStack environment:

```bash
# terminal 1: the official GELLO publisher (from the teleoperation repo)
ros2 launch franka_gello_state_publisher main.launch.py config_file:=franka_gello_duo.yaml
# terminal 2: this sim, subscribing to it
python main.py --input gello
```

Topic contract (per-arm namespace from that launch config):
`<ns>/gello/joint_states` (`sensor_msgs/JointState`, 7 joint angles, already
offset/sign-corrected and clamped to the real FR3 limits) and
`<ns>/gripper/gripper_client/target_gripper_width_percent`
(`std_msgs/Float32`, 0.0–1.0). The gripper open/closed direction (1.0 =
open) is inferred from the topic name and not yet confirmed against real
hardware — flag it if it's inverted on your rig
(`teleop/config.py`: `GELLO_GRIPPER_CLOSE_BELOW`/`GELLO_GRIPPER_OPEN_ABOVE`).

## Unified ROS 2 teleop (`--input ros_teleop`)

Splits teleoperation into two processes connected by ROS 2 topics: a
**publisher node** reads the physical device and publishes device-agnostic
Cartesian commands; the sim (`--input ros_teleop`) subscribes and applies
them through the exact same IK/grasp/base-drive code the local modes use.
Use it when the device and the sim must live in different processes,
containers, or machines. Two publishers ship in `teleop_ros2/`
(keyboard and gamepad); both are baked into the eval image:

```bash
# terminal 1: the sim as consumer
python main.py --input ros_teleop
# terminal 2: a publisher (device attached to THIS machine)
ros2 run keyboard_teleop_publisher keyboard_teleop_publisher
# or: ros2 run gamepad_teleop_publisher gamepad_teleop_publisher
# no device handy? each publisher has a scripted self-test: --pattern 60
```

Topic contract: `/cmd_vel` (`geometry_msgs/Twist`, base — REP-103
`base_link` frame, `linear.z` repurposed for the spine lift rate),
`<side>/teleop_cmd` (`geometry_msgs/Twist`, per-arm Cartesian TCP twist),
`<side>/gripper_cmd` (`std_msgs/Float32`, >0.5 = close intent). `/cmd_vel`
matches the topic EBiM_Challenge's own Isaac Sim test commands already use.
GELLO is intentionally not part of this contract — it stays joint-space and
IK-free (`--input gello` above). Note: contact rumble/haptics only exist in
the local modes; the ROS contract has no haptic feedback channel yet.

**Verification status**: the full chain (publisher → topics → sim) has been
verified end-to-end with the publishers' `--pattern` synthetic self-test
(resulting TCP motion bit-identical to raw topic publishing). Physical
keyboard/gamepad runs over ROS are in community testing — reports welcome.

## Self-testing without ROS

```bash
./start.sh --no-viewer                    # headless smoke test
./start.sh --randomize-board              # fixture randomization, same
                                          # distribution the client uses
./start.sh --display-code TEST1234        # preview the one-time-code plate
```

Every mode also accepts `--help` for the full per-module option list.

## Troubleshooting

- **"init/smoke ok"** = environment is healthy
- **`[keyboard] held-key backend: press-timeout fallback (...)`** (Linux) —
  held keys will cut out; the message names the cause. Usually python-xlib
  is missing (the launcher auto-installs it on the next run) or the session
  has no X server.
- **`[mnet] WARNING: evidence camera at N fps`** — your rendering cannot
  reach the client's 25 fps minimum (it will refuse the session). Typical
  cause: WSL2 or a container without GPU access. Run the eval on native
  Linux, or enable the GPU blocks in `release/compose.yaml`
  (nvidia-container-toolkit).
- **"OpenGL version 1.5 or higher required"** (WSL2) — usually a stale
  `LIBGL_ALWAYS_INDIRECT=1` or a manual `DISPLAY=<ip>:0` left in `~/.bashrc`
  from old X-server setups: remove them (WSLg sets `DISPLAY` itself). Then
  try `wsl --update` + `wsl --shutdown` from Windows. Last resort:
  `LIBGL_ALWAYS_SOFTWARE=1 ./start.sh` (software rendering, slower).
- **"X11: Failed to open display localhost:N.0" / "could not initialize
  GLFW"** (WSL2) — an SSH-forwarded `DISPLAY` is set in this shell (sshd
  sets `localhost:10.0`-style values); WSLg's real display is `:0`. The
  launch scripts rewrite that pattern automatically; when running things by
  hand, prefix the command with `DISPLAY=:0`.
- **Window opens then goes black / crashes** (WSL2, hybrid-graphics laptop)
  — the integrated GPU's OpenGL support through Mesa's D3D12 translation
  layer can segfault mid-render. `start.sh`/`eval.sh` auto-detect a
  discrete NVIDIA/AMD GPU and steer rendering to it; if you still hit this,
  set it manually: `export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"` (or
  `"AMD"`/`"Radeon"`, matching your GPU name) before running.
- **`FormFactorUnavailable`** (VR) — the streaming app is not connected or the
  headset is not being worn
- **"Camera topic has no publishers"** (client) — start `./eval.sh sim` before
  `./eval.sh client`
- **No window from Docker on native Linux** — run `xhost +local:docker` once
  per session (WSL2 needs nothing; WSLg handles the display)
- Scoring uses the overhead evidence camera, not your viewer perspective

## Directory layout

```
robotiq_duo_full_scene_minimal_core/   simulator (entry: main.py, code: teleop/)
mnet_client-ros_2/                     official ManipulationNet ROS 2 client (vendored)
teleop_ros2/                           ROS 2 teleop publisher packages (keyboard, gamepad)
start.bat / start.sh                   Path A: one-click native launchers (Windows / Ubuntu)
eval.sh                                Path B: ManipulationNet evaluation stack (Docker + ROS 2)
docker-run.sh                          Path C: cross-platform Docker test (no ROS)
```

## License & attribution

Copyright (c) 2026 **2houyuhang**. Licensed under the
[Apache License 2.0](LICENSE) — the source is open; keep the copyright and
attribution notices when using or modifying it.

`mnet_client-ros_2` is the official [ManipulationNet](https://manipulation-net.org)
client (Apache-2.0), vendored unmodified with unrelated task assets removed.
Scene and robot assets are provided for research and benchmark use.
