#!/usr/bin/env python3
"""
按照布局图摆放11个桌子
"""

import argparse
import os

print("="*80)
print("11个桌子布局场景")
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
from isaaclab.assets import AssetBaseCfg
from isaaclab.utils import configclass
import isaaclab.sim as sim_utils

print("✓ 模块导入完成")

# 获取文件路径
script_dir = os.path.dirname(__file__)
table_path = os.path.join(script_dir, "assets/table_edit.usd")

# 定义所有字母路径并检查文件存在
letter_paths = {}
for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
    letter_file = os.path.join(script_dir, f"assets/{letter}_edit.usd")
    if not os.path.exists(letter_file):
        raise FileNotFoundError(f"找不到字母文件: {letter_file}")
    letter_paths[letter] = letter_file

# 定义餐具路径并检查文件存在
cutlery_paths = {}
for item in ['bowl', 'plate', 'spoon']:
    cutlery_file = os.path.join(script_dir, f"assets/{item}.usd")
    if not os.path.exists(cutlery_file):
        raise FileNotFoundError(f"找不到餐具文件: {cutlery_file}")
    cutlery_paths[item] = cutlery_file

if not os.path.exists(table_path):
    raise FileNotFoundError(f"找不到桌子文件: {table_path}")

print(f"✓ 找到桌子文件: {table_path}")
print(f"✓ 找到9个字母文件 (A-I)")
print(f"✓ 找到3个餐具文件 (bowl, plate, spoon)")


# 场景配置
@configclass
class MultiTableSceneCfg(InteractiveSceneCfg):
    """11个桌子的场景配置"""
    
    # 地面
    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.GroundPlaneCfg(size=(20.0, 20.0)),
    )
    
    # 光照
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=5000.0, color=(1.0, 1.0, 1.0)),
    )
    
    # 添加额外的直射光
    distant_light = AssetBaseCfg(
        prim_path="/World/DistantLight",
        spawn=sim_utils.DistantLightCfg(intensity=3000.0, color=(1.0, 1.0, 1.0), angle=0.5),
    )
    
    # 桌子布局（根据图示）
    # 假设：桌子间距1.5m，左右列间距2.5m，走道宽度
    
    # 左列5个桌子（X=-2.0）
    table_left_1 = AssetBaseCfg(  # 灰色（餐具桌）
        prim_path="{ENV_REGEX_NS}/Table_Left_1",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(-2.0, 3.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_left_2 = AssetBaseCfg(  # 字母A
        prim_path="{ENV_REGEX_NS}/Table_Left_2",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(-2.0, 1.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_left_3 = AssetBaseCfg(  # 字母C
        prim_path="{ENV_REGEX_NS}/Table_Left_3",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(-2.0, 0.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_left_4 = AssetBaseCfg(  # 字母E
        prim_path="{ENV_REGEX_NS}/Table_Left_4",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(-2.0, -1.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_left_5 = AssetBaseCfg(  # 字母G
        prim_path="{ENV_REGEX_NS}/Table_Left_5",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(-2.0, -3.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    # 右列5个桌子（X=2.0）
    table_right_1 = AssetBaseCfg(  # 黄色（空桌）
        prim_path="{ENV_REGEX_NS}/Table_Right_1",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(2.0, 3.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_right_2 = AssetBaseCfg(  # 字母B
        prim_path="{ENV_REGEX_NS}/Table_Right_2",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(2.0, 1.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_right_3 = AssetBaseCfg(  # 字母D
        prim_path="{ENV_REGEX_NS}/Table_Right_3",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(2.0, 0.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_right_4 = AssetBaseCfg(  # 字母F
        prim_path="{ENV_REGEX_NS}/Table_Right_4",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(2.0, -1.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    table_right_5 = AssetBaseCfg(  # 字母H
        prim_path="{ENV_REGEX_NS}/Table_Right_5",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(2.0, -3.0, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    # 顶部中间1个桌子（小方框）
    table_top_center = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table_Top_Center",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.0, 4.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )
    
    # 底部中间1个桌子（字母I）
    table_bottom_center = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table_Bottom_Center",
        spawn=sim_utils.UsdFileCfg(usd_path=table_path, scale=(0.001, 0.001, 0.001)),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=(0.0, -4.5, 0.7),  # Z改为0.7
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    )

# 场景配置实例
scene_cfg = MultiTableSceneCfg(num_envs=args.num_envs, env_spacing=10.0)

# 动态添加9个字母配置
# 字母相对于桌子的偏移: X+0.35, Y-0.45, Z=0.761（桌子在0.7，字母高度+0.061）
letter_configs = {
    'A': {'table_pos': (-2.0, 1.5, 0.7)},
    'B': {'table_pos': (2.0, 1.5, 0.7)},
    'C': {'table_pos': (-2.0, 0.0, 0.7)},
    'D': {'table_pos': (2.0, 0.0, 0.7)},
    'E': {'table_pos': (-2.0, -1.5, 0.7)},
    'F': {'table_pos': (2.0, -1.5, 0.7)},
    'G': {'table_pos': (-2.0, -3.0, 0.7)},
    'H': {'table_pos': (2.0, -3.0, 0.7)},
    'I': {'table_pos': (0.0, -4.5, 0.7)},
}

for letter, config in letter_configs.items():
    tx, ty, tz = config['table_pos']
    letter_pos = (tx + 0.35, ty - 0.45, tz + 0.061)  # 字母往右下偏移，高度+0.061
    
    setattr(scene_cfg, f'letter_{letter}', AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Letter_" + letter,
        spawn=sim_utils.UsdFileCfg(
            usd_path=letter_paths[letter],
            scale=(0.001, 0.001, 0.001),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=(0.0, 0.0, 0.0),  # 黑色
                emissive_color=(0.0, 0.0, 0.0),  # 无发光
                metallic=0.0,
                roughness=0.8,  # 增加粗糙度，减少反光
            ),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=letter_pos,
            rot=(0.7071, 0.7071, 0.0, 0.0),
        ),
    ))

print("✓ 场景配置创建完成（包含9个字母）")

# 动态添加3个餐具配置（在左上角餐具桌上）
# 餐具桌位置: (-2.0, 3.0, 0.7)
ikea_configs = {
    'bowl': {'offset': (0.45, -0.3, 0.15), 'color': (1.0, 0.0, 0.0), 'rot': (0.5, 0.5, 0.5, 0.5)},    # 红色，X90+Y90
    'plate': {'offset': (0.2, -0.3, 0.08), 'color': (1.0, 1.0, 0.0), 'rot': (0.5, 0.5, 0.5, 0.5)},   # 黄色，X90+Y90
    'spoon': {'offset': (0.4, -0.3, 0.07), 'color': (0.0, 0.0, 1.0), 'rot': (0.0, 0.7071, 0.0, 0.7071)},   # 蓝色，Y90
}

ikea_table_pos = (-2.0, 3.0, 0.7)  # 餐具桌位置

for item, config in ikea_configs.items():
    offset_x, offset_y, offset_z = config['offset']
    item_pos = (ikea_table_pos[0] + offset_x, ikea_table_pos[1] + offset_y, ikea_table_pos[2] + offset_z)
    
    setattr(scene_cfg, f'ikea_{item}', AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Ikea_" + item.capitalize(),
        spawn=sim_utils.UsdFileCfg(
            usd_path=cutlery_paths[item],
            scale=(0.001, 0.001, 0.001),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=config['color'],  # 红黄蓝
                metallic=0.2,
                roughness=0.4,
            ),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=item_pos,
            rot=config['rot'],  # 每个餐具的旋转
        ),
    ))

print("✓ 场景配置创建完成（包含9个字母 + 3个餐具）")

# 创建仿真上下文
sim_cfg = sim_utils.SimulationCfg(dt=1/60, device="cuda:0")
sim = SimulationContext(sim_cfg)
sim.set_camera_view(eye=[0.0, 0.0, 15.0], target=[0.0, 0.0, 0.0])  # 从上方俯视

print("✓ 仿真上下文创建完成")

# 创建场景（使用上面已配置好字母的scene_cfg）
scene = InteractiveScene(scene_cfg)

print("✓ 场景创建完成")

# 物理初始化
sim.reset()
scene.reset()

# 强制设置所有字母为黑色材质
print("正在设置字母颜色...")
from pxr import Usd, UsdShade, Sdf
stage = sim.stage

for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
    letter_prim_path = f"/World/envs/env_0/Letter_{letter}"
    letter_prim = stage.GetPrimAtPath(letter_prim_path)
    
    if letter_prim.IsValid():
        # 遍历所有子节点寻找Mesh
        for child_prim in Usd.PrimRange(letter_prim):
            if child_prim.IsA(UsdShade.Material):
                material = UsdShade.Material(child_prim)
                shader = material.GetSurfaceOutput().GetConnectedSource()[0]
                if shader:
                    shader_prim = shader.GetPrim()
                    # 设置黑色
                    if shader_prim.HasAttribute("inputs:diffuseColor"):
                        shader_prim.GetAttribute("inputs:diffuseColor").Set((0.0, 0.0, 0.0))

print("✓ 物理初始化和字母颜色设置完成")
print("\n开始仿真...")
print("提示: 11个桌子 + 9个字母 + 3个餐具已按照布局图摆放")
print("  - 左列5个桌子: 餐具桌(红bowl/黄plate/蓝spoon), A, C, E, G")
print("  - 右列5个桌子: 空桌, B, D, F, H")
print("  - 顶部中间: 1个空桌")
print("  - 底部中间: I")
print("  - 所有字母为黑色，餐具为红黄蓝")
print("按 Ctrl+C 退出\n")

# 仿真循环
count = 0
scene_saved = False
try:
    while simulation_app.is_running():
        # 步进仿真
        sim.step()
        scene.update(sim.cfg.dt)
        
        count += 1
        if count % 200 == 0:
            print(f"步数 {count} - 场景运行正常")
        
        # 在第1000步保存场景
        if count == 1000 and not scene_saved:
            from pxr import Usd
            save_path = os.path.join(script_dir, "assets/complete_scene_11_tables.usd")
            sim.stage.Export(save_path)
            print(f"\n✓ 完整场景已保存到: {save_path}")
            print(f"   包含: 11个桌子 + 9个字母 + 3个餐具\n")
            scene_saved = True

except KeyboardInterrupt:
    print("\n仿真已停止")
finally:
    simulation_app.close()
