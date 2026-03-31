#!/usr/bin/env python3
"""
场景中包含机器人和桌子的演示
"""

import argparse
import os

print("="*80)
print("机器人与桌子场景演示")
print("="*80)

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=1, help="环境数量")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 导入Isaac Lab模块
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.assets import AssetBaseCfg, RigidObjectCfg, ArticulationCfg
from isaaclab.utils import configclass
from isaaclab.actuators import ImplicitActuatorCfg
import isaaclab.sim as sim_utils

print("✓ 模块导入完成")

# 获取文件路径
table_usd_path = os.path.join(os.path.dirname(__file__), "assets/table.usd")
robot_usd_path = "/home/ju.dong/Desktop/franka_description/urdfs/mobile_fr3_duo_v0_2_franka_hand.usd"

if not os.path.exists(table_usd_path):
    raise FileNotFoundError(f"找不到桌子文件: {table_usd_path}")
if not os.path.exists(robot_usd_path):
    raise FileNotFoundError(f"找不到机器人文件: {robot_usd_path}")
    
print(f"✓ 找到桌子文件: {table_usd_path}")
print(f"✓ 找到机器人文件: {robot_usd_path}")

# 机械臂初始姿态（垂直向上收起）
initial_joint_pos = {
    "left_fr3v2_joint1": 0.0,
    "left_fr3v2_joint2": -1.5,
    "left_fr3v2_joint3": 0.0,
    "left_fr3v2_joint4": -2.2,
    "left_fr3v2_joint5": 0.0,
    "left_fr3v2_joint6": 1.5,
    "left_fr3v2_joint7": 0.785,
    "right_fr3v2_joint1": 0.0,
    "right_fr3v2_joint2": -1.5,
    "right_fr3v2_joint3": 0.0,
    "right_fr3v2_joint4": -2.2,
    "right_fr3v2_joint5": 0.0,
    "right_fr3v2_joint6": 1.5,
    "right_fr3v2_joint7": 0.785,
}

# 创建场景配置
@configclass
class RobotTableSceneCfg(InteractiveSceneCfg):
    """机器人与桌子的场景配置"""
    
    # 地面
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(
            physics_material=sim_utils.RigidBodyMaterialCfg(
                static_friction=2.0,
                dynamic_friction=1.5,
                restitution=0.0,
            ),
        ),
    )
    
    # 光照
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(1.0, 1.0, 1.0)),
    )
    
    # 桌子 - 作为静态装饰物
    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        spawn=sim_utils.UsdFileCfg(
            usd_path=table_usd_path,
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(1.5, 0.0, 0.0),  # 桌子在机器人前方1.5米
            rot=(1.0, 0.0, 0.0, 0.0),
        ),
    )

print("✓ 场景配置类创建完成")

# 创建场景实例
scene_cfg = RobotTableSceneCfg(num_envs=args.num_envs, env_spacing=3.0)

# 添加机器人配置到场景实例
scene_cfg.robot = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=sim_utils.UsdFileCfg(usd_path=robot_usd_path),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        joint_pos=initial_joint_pos,
    ),
    actuators={
        "steering_joints": ImplicitActuatorCfg(
            joint_names_expr=["tmrv0_2_joint_0", "tmrv0_2_joint_2"],
            stiffness=500.0,
            damping=50.0,
            effort_limit=200.0,
        ),
        "drive_joints": ImplicitActuatorCfg(
            joint_names_expr=["tmrv0_2_joint_1", "tmrv0_2_joint_3", ".*caster.*", "rocker_arm_joint"],
            stiffness=0.0,
            damping=50.0,
            effort_limit=500.0,
            velocity_limit=20.0,
        ),
        "arms": ImplicitActuatorCfg(
            joint_names_expr=[".*fr3v2_joint[1-7]"],
            stiffness=5000.0,
            damping=500.0,
            effort_limit=200.0,
        ),
        "grippers": ImplicitActuatorCfg(
            joint_names_expr=[".*finger.*"],
            stiffness=200.0,
            damping=20.0,
            effort_limit=50.0,
        ),
    },
)

# 创建仿真上下文
sim_cfg = sim_utils.SimulationCfg(
    dt=0.005,
    device="cuda:0",
    gravity=(0.0, 0.0, -9.81),
)
sim = SimulationContext(sim_cfg)
sim.set_camera_view([3.5, 3.5, 2.5], [0.0, 0.0, 0.5])

print("✓ 仿真上下文创建完成")

# 创建场景
scene = InteractiveScene(scene_cfg)
print("✓ 场景创建完成")

# 获取机器人和桌子
robot = scene["robot"]
table = scene["table"]

# 物理初始化
sim.reset()
scene.reset()
print("✓ 物理初始化完成")

# 稳定机器人
print("稳定机器人中...")
for i in range(500):
    robot.write_data_to_sim()
    sim.step()
    scene.update(sim.cfg.dt)
    if i % 100 == 0:
        print(f"  稳定中... {i}/500")
print("✓ 机器人已稳定")

print("\n" + "="*80)
print("✓ 场景初始化完成!")
print("="*80)
print("\n场景内容:")
print(f"  - 机器人位置: (0.0, 0.0, 0.0)")
print(f"  - 桌子位置: (1.5, 0.0, 0.0)")
print("\n提示: 按 Ctrl+C 退出\n")

# 仿真循环
count = 0
try:
    while simulation_app.is_running():
        # 保持机器人姿态
        robot.set_joint_position_target(robot.data.default_joint_pos)
        robot.write_data_to_sim()
        
        # 步进仿真
        sim.step()
        scene.update(sim.cfg.dt)
        
        count += 1
        if count % 500 == 0:
            print(f"仿真步数: {count}")
            robot_pos = robot.data.root_pos_w[0].cpu().numpy()
            table_pos = table.data.root_pos_w[0].cpu().numpy()
            print(f"  机器人位置: [{robot_pos[0]:.3f}, {robot_pos[1]:.3f}, {robot_pos[2]:.3f}]")
            print(f"  桌子位置: [{table_pos[0]:.3f}, {table_pos[1]:.3f}, {table_pos[2]:.3f}]")

except KeyboardInterrupt:
    print("\n✓ 用户停止")
except Exception as e:
    print(f"\n❌ 运行时错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    simulation_app.close()
    print("✓ 仿真关闭")
