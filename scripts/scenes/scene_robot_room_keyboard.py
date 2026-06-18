#!/usr/bin/env python3
"""Launch the physics robot room in Isaac Sim with the mobile FR3 placed."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

COMMON_DIR = Path(__file__).resolve().parents[1] / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from path_utils import asset_path, franka_urdf_path

ISAACSIM_EXPERIENCES = {
    "base": "/isaac-sim/apps/isaacsim.exp.base.kit",
    "full": "/isaac-sim/apps/isaacsim.exp.full.kit",
}
ROS2_BRIDGE_ROOT = Path("/isaac-sim/exts/isaacsim.ros2.bridge")
ROS2_ENV_READY_VAR = "IROS_ROS2_BRIDGE_ENV_READY"
INSIDE_KIT_ENV_VAR = "IROS_SCENE_LAUNCH_INSIDE_KIT"
INNER_ARGV_ENV_VAR = "IROS_SCENE_LAUNCH_ARGV"
ISAACSIM_LAUNCHER = Path("/isaac-sim/isaac-sim.sh")
TASK_ROBOT_POSES = {
    "task1": {"position": (4.4, -2.5, 0.0), "yaw": 90.0},
    "task2": {"position": (4.4, 2.6, 0.0), "yaw": -90.0},
    "task3": {"position": (-4.6, 2.7, 0.0), "yaw": -90.0},
}


def parse_args() -> argparse.Namespace:
    argv = None
    if os.environ.get(INSIDE_KIT_ENV_VAR) == "1":
        raw_argv = os.environ.get(INNER_ARGV_ENV_VAR)
        if raw_argv:
            argv = json.loads(raw_argv)

    parser = argparse.ArgumentParser(
        description=(
            "Launch robot_room_physics.usd with the mobile FR3 in Isaac Sim."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--room-usd",
        type=Path,
        default=None,
        help=(
            "Room USD to reference. Defaults to assets/robot_room_physics.usd."
        ),
    )
    parser.add_argument(
        "--robot-usd",
        type=Path,
        default=None,
        help="Robot USD to reference. Defaults to the Franka mobile FR3 USD.",
    )
    parser.add_argument(
        "--task",
        choices=tuple(TASK_ROBOT_POSES),
        default="task3",
        help="Task preset used for the robot spawn position.",
    )
    parser.add_argument(
        "--robot-x",
        type=float,
        default=None,
        help="Override the preset robot X position.",
    )
    parser.add_argument(
        "--robot-y",
        type=float,
        default=None,
        help="Override the preset robot Y position.",
    )
    parser.add_argument(
        "--robot-z",
        type=float,
        default=None,
        help="Override the preset robot Z position.",
    )
    parser.add_argument(
        "--robot-yaw",
        type=float,
        default=None,
        help="Override the preset robot yaw in degrees.",
    )
    parser.add_argument(
        "--autoplay",
        action="store_true",
        help="Start the Isaac Sim timeline immediately after loading.",
    )
    parser.add_argument(
        "--experience",
        choices=tuple(ISAACSIM_EXPERIENCES),
        default="base",
        help="Isaac Sim Kit experience to launch.",
    )
    parser.add_argument(
        "--ros2-bridge",
        choices=("disabled", "fastdds", "cyclonedds"),
        default="disabled",
        help="Enable the Isaac Sim ROS2 bridge with the selected RMW.",
    )
    parser.add_argument(
        "--ros-distro",
        choices=("jazzy", "humble"),
        default="jazzy",
        help="Bundled ROS2 bridge distro to use when ROS2 is enabled.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Launch Isaac Sim without a GUI window.",
    )
    parser.add_argument(
        "--inside-kit",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def resolve_usd_path(selection: Path | None, default_path: Path) -> Path:
    if selection is None:
        return default_path

    candidate = selection.expanduser()
    if candidate.is_absolute() or candidate.is_file():
        return candidate
    return asset_path(*candidate.parts)


def yaw_to_quat(yaw_degrees: float) -> tuple[float, float, float, float]:
    half_yaw = math.radians(yaw_degrees) * 0.5
    return (math.cos(half_yaw), 0.0, 0.0, math.sin(half_yaw))


def resolve_robot_position(
    args: argparse.Namespace,
) -> tuple[float, float, float]:
    preset_x, preset_y, preset_z = TASK_ROBOT_POSES[args.task]["position"]
    return (
        preset_x if args.robot_x is None else args.robot_x,
        preset_y if args.robot_y is None else args.robot_y,
        preset_z if args.robot_z is None else args.robot_z,
    )


def resolve_robot_yaw(args: argparse.Namespace) -> float:
    if args.robot_yaw is not None:
        return args.robot_yaw
    return TASK_ROBOT_POSES[args.task]["yaw"]


def configure_ros2_bridge_env(args: argparse.Namespace) -> None:
    if args.ros2_bridge == "disabled":
        return

    bridge_lib = ROS2_BRIDGE_ROOT / args.ros_distro / "lib"
    if not bridge_lib.is_dir():
        raise FileNotFoundError(
            f"ROS2 bridge library path not found: {bridge_lib}"
        )

    rmw_by_bridge = {
        "fastdds": "rmw_fastrtps_cpp",
        "cyclonedds": "rmw_cyclonedds_cpp",
    }
    os.environ["ROS_DISTRO"] = args.ros_distro
    os.environ["RMW_IMPLEMENTATION"] = rmw_by_bridge[args.ros2_bridge]
    os.environ.setdefault("ROS_LOG_DIR", "/isaac-sim/kit/logs/ros")
    existing_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    ld_paths = [str(bridge_lib)]
    if existing_ld_path:
        ld_paths.append(existing_ld_path)
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)

    if os.environ.get(ROS2_ENV_READY_VAR) != "1":
        env = os.environ.copy()
        env[ROS2_ENV_READY_VAR] = "1"
        os.execvpe(sys.executable, [sys.executable, *sys.argv], env)


def enable_ros2_bridge(app: Any, args: argparse.Namespace) -> None:
    if args.ros2_bridge == "disabled":
        return

    import omni.kit.app

    extension_manager = omni.kit.app.get_app().get_extension_manager()
    extension_manager.set_extension_enabled_immediate(
        "isaacsim.ros2.bridge",
        True,
    )
    for _ in range(10):
        app.update()
    print(
        f"ROS2 bridge: {args.ros_distro} / {os.environ['RMW_IMPLEMENTATION']}"
    )


def launch_isaac_sim(args: argparse.Namespace) -> None:
    if not ISAACSIM_LAUNCHER.is_file():
        raise FileNotFoundError(
            f"Isaac Sim launcher not found: {ISAACSIM_LAUNCHER}"
        )

    configure_ros2_bridge_env(args)

    command = [
        str(ISAACSIM_LAUNCHER),
        ISAACSIM_EXPERIENCES[args.experience],
    ]
    if args.headless:
        command.append("--no-window")
    command.extend(["--exec", str(Path(__file__).resolve()), "--inside-kit"])
    env = os.environ.copy()
    env[INSIDE_KIT_ENV_VAR] = "1"
    env[INNER_ARGV_ENV_VAR] = json.dumps(
        [arg for arg in sys.argv[1:] if arg != "--inside-kit"]
    )
    os.chdir("/isaac-sim")
    os.execvpe(command[0], command, env)


def set_xform(
    prim: Any,
    position: tuple[float, float, float],
    rotation: tuple[float, float, float, float],
) -> None:
    from pxr import Gf as pxr_gf
    from pxr import UsdGeom as pxr_usd_geom

    Gf: Any = pxr_gf
    UsdGeom: Any = pxr_usd_geom

    xform = UsdGeom.Xformable(prim)
    xform.ClearXformOpOrder()
    xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble).Set(
        Gf.Vec3d(*position)
    )
    xform.AddOrientOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Quatf(rotation[0], rotation[1], rotation[2], rotation[3])
    )


def reference_usd(
    stage: Any,
    prim_path: str,
    usd_path: Path,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0),
    reset_asset_xform: bool = False,
) -> Any:
    from pxr import UsdGeom as pxr_usd_geom

    UsdGeom: Any = pxr_usd_geom

    parent_prim = UsdGeom.Xform.Define(stage, prim_path).GetPrim()
    set_xform(parent_prim, position, rotation)

    asset_prim = UsdGeom.Xform.Define(stage, f"{prim_path}/Asset").GetPrim()
    asset_prim.GetReferences().AddReference(str(usd_path.resolve()))
    if reset_asset_xform:
        set_xform(asset_prim, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0))
    return asset_prim


def build_stage(
    app: Any,
    room_path: Path,
    robot_path: Path,
    robot_position: tuple[float, float, float],
    robot_rotation: tuple[float, float, float, float],
    robot_yaw: float,
) -> Any:
    import omni.usd
    from pxr import UsdGeom as pxr_usd_geom
    from pxr import UsdLux as pxr_usd_lux

    UsdGeom: Any = pxr_usd_geom
    UsdLux: Any = pxr_usd_lux

    context = omni.usd.get_context()
    context.new_stage()
    for _ in range(10):
        app.update()

    stage = context.get_stage()
    if stage is None:
        raise RuntimeError("Could not create an Isaac Sim stage.")

    stage.SetFramesPerSecond(60.0)
    stage.SetTimeCodesPerSecond(60.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    UsdGeom.Scope.Define(stage, "/World/Environment")

    reference_usd(
        stage,
        "/World/Environment/RobotRoom",
        room_path,
        reset_asset_xform=True,
    )
    reference_usd(
        stage,
        "/World/Robot",
        robot_path,
        robot_position,
        robot_rotation,
    )

    dome = UsdLux.DomeLight.Define(stage, "/World/Light")
    dome.CreateIntensityAttr(3000.0)

    camera = UsdGeom.Camera.Define(stage, "/World/Camera")
    set_xform(
        camera.GetPrim(),
        (robot_position[0] + 3.5, robot_position[1] + 3.5, 2.5),
        (0.9238795, -0.3826834, 0.0, 0.0),
    )
    camera.CreateFocalLengthAttr(18.0)

    for _ in range(10):
        app.update()

    print("=" * 80)
    print("Robot room loaded in Isaac Sim")
    print("=" * 80)
    print(f"Room USD: {room_path}")
    print(f"Robot USD: {robot_path}")
    print(
        "Robot start: "
        f"({robot_position[0]:.3f}, {robot_position[1]:.3f}, "
        f"{robot_position[2]:.3f})"
    )
    print(f"Robot yaw: {robot_yaw:.1f} deg")
    return stage


def main() -> None:
    args = parse_args()
    room_path = resolve_usd_path(
        args.room_usd,
        asset_path("robot_room_physics.usd"),
    )
    robot_path = resolve_usd_path(
        args.robot_usd,
        franka_urdf_path("mobile_fr3_duo_v0_2_franka_hand.usd"),
    )

    if not room_path.is_file():
        raise FileNotFoundError(f"Room USD not found: {room_path}")
    if not robot_path.is_file():
        raise FileNotFoundError(f"Robot USD not found: {robot_path}")

    robot_position = resolve_robot_position(args)
    robot_yaw = resolve_robot_yaw(args)

    if not args.inside_kit and os.environ.get(INSIDE_KIT_ENV_VAR) != "1":
        launch_isaac_sim(args)
        return

    import omni.kit.app

    app = omni.kit.app.get_app()
    try:
        build_stage(
            app,
            room_path=room_path,
            robot_path=robot_path,
            robot_position=robot_position,
            robot_rotation=yaw_to_quat(robot_yaw),
            robot_yaw=robot_yaw,
        )
        enable_ros2_bridge(app, args)

        import omni.timeline

        timeline = omni.timeline.get_timeline_interface()
        if args.autoplay:
            timeline.play()
            print("Timeline: playing")
        else:
            timeline.stop()
            print(
                "Timeline: paused. Click Play in the Isaac Sim GUI to start."
            )
        print("Close the Isaac Sim GUI window to exit.")
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()
