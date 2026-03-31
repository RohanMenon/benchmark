# Robot Lab - Isaac Sim 仿真场景

基于 Isaac Lab 的移动双臂机器人仿真项目，包含场景设计、键盘控制等功能。

## 项目结构

```
robot_lab/
├── assets/                          # 资源文件
│   ├── table_edit.usd              # 桌子模型
│   ├── A_edit.usd ~ I_edit.usd     # 字母A-I模型
│   ├── bowl.usd                    # 碗模型
│   ├── plate.usd                   # 盘子模型
│   ├── spoon.usd                   # 勺子模型
│   ├── complete_scene_11_tables.usd           # 保存的完整场景（11桌）
│   └── complete_scene_with_robot_keyboard.usd # 保存的机器人场景
├── keyboard_control.py             # 原始键盘控制脚本（单机器人）
├── scene_11_tables.py              # 11个桌子 + 9个字母 + 3个餐具
├── scene_robot_tables.py           # 10个桌子 + 机器人（无控制）
├── scene_robot_keyboard.py         # 完整场景 + 键盘控制 ⭐推荐
├── test_table_letter.py            # 测试脚本：单桌子 + 字母A
├── test_table_cutlery.py           # 测试脚本：单桌子 + 3个餐具
└── inspect_usd.py                  # USD文件检查工具
```

## 主要脚本说明

### 1. `scene_robot_keyboard.py` ⭐推荐
**完整场景 + 键盘控制**

包含完整的仿真环境：
- 10个桌子（摆放成两列）
- 9个字母（A-I，黑色）
- 3个餐具（红碗/黄盘/蓝勺）
- 1个可控移动双臂机器人

**运行方式：**
```bash
source ~/.bashrc && conda activate isaaclab && python scene_robot_keyboard.py
```

**键盘控制：**
- `W` - 向前移动
- `S` - 向后移动
- `A` - 向左转（自动前进）
- `D` - 向右转（自动前进）
- `ESC` / `Ctrl+C` - 退出

**特性：**
- 无需点击窗口即可控制（使用pynput）
- 机器人初始姿态稳定（机械臂收起）
- 自动在1000步后保存场景为USD文件

---

### 2. `scene_11_tables.py`
**11个桌子布局场景**

包含11个桌子 + 9个字母 + 3个餐具，无机器人。

**运行方式：**
```bash
source ~/.bashrc && conda activate isaaclab && python scene_11_tables.py
```

**布局：**
- 左列5个桌子：餐具桌（含碗/盘/勺）、A、C、E、G
- 右列5个桌子：空桌、B、D、F、H
- 顶部中间：空桌
- 底部中间：I

---

### 3. `keyboard_control.py`
**原始键盘控制脚本**

仅包含单个移动双臂机器人，用于测试基础控制功能。

**运行方式：**
```bash
source ~/.bashrc && conda activate isaaclab && python keyboard_control.py
```

---

### 4. 测试脚本

#### `test_table_letter.py`
测试单个桌子和字母A的摆放、缩放、旋转。

#### `test_table_cutlery.py`
测试单个桌子和3个餐具的摆放、旋转、颜色。

**运行方式：**
```bash
source ~/.bashrc && conda activate isaaclab && python test_table_letter.py
source ~/.bashrc && conda activate isaaclab && python test_table_cutlery.py
```

---

## 资源文件配置参数

### 桌子（table_edit.usd）
- **Scale**: `(0.001, 0.001, 0.001)`
- **Rotation**: `(0.7071, 0.7071, 0.0, 0.0)` - X轴90度 + Y轴180度，让桌子站立
- **Z Position**: `0.7` - 桌腿在地面上

### 字母（A_edit.usd ~ I_edit.usd）
- **Scale**: `(0.001, 0.001, 0.001)`
- **Rotation**: `(0.7071, 0.7071, 0.0, 0.0)` - X轴90度 + Y轴180度，平放在桌面
- **Color**: 黑色 `(0.0, 0.0, 0.0)`
- **Position Offset**: 
  - 相对桌子中心：X +0.35, Y -0.45
  - Z高度：桌子Z + 0.061 = 0.761

### 餐具（bowl.usd, plate.usd, spoon.usd）
- **Scale**: `(0.001, 0.001, 0.001)`
- **Colors**:
  - Bowl（碗）: 红色 `(1.0, 0.0, 0.0)`
  - Plate（盘子）: 黄色 `(1.0, 1.0, 0.0)`
  - Spoon（勺子）: 蓝色 `(0.0, 0.0, 1.0)`
- **Rotations**:
  - Bowl: X轴90度 + Y轴90度 `(0.5, 0.5, 0.5, 0.5)`
  - Plate: X轴90度 + Y轴90度 `(0.5, 0.5, 0.5, 0.5)`
  - Spoon: Y轴90度 `(0.0, 0.7071, 0.0, 0.7071)`
- **Position Offsets** (相对餐具桌):
  - Bowl: X +0.45, Y -0.3, Z +0.15
  - Plate: X +0.2, Y -0.3, Z +0.08
  - Spoon: X +0.4, Y -0.3, Z +0.07

### 机器人（mobile_fr3_duo_v0_2_franka_hand.usd）
- **Position**: `(0.0, 4.5, 0.0)` - 顶部中间位置
- **Initial Joint Config**: 双臂收起姿态，防止前倾
- **Actuators**:
  - 转向关节：位置控制（高刚度）
  - 驱动轮：速度控制（低刚度）
  - 机械臂：位置控制（中等刚度）

---

## 技术要点

### 1. 坐标系统
- **X轴**: 左右方向（左负右正）
- **Y轴**: 前后方向（后负前正）
- **Z轴**: 上下方向（下负上正）

### 2. 旋转表示
使用四元数 `(x, y, z, w)` 表示旋转：
- X轴90度: `(0.7071, 0.0, 0.0, 0.7071)`
- Y轴90度: `(0.0, 0.7071, 0.0, 0.7071)`
- X90+Y90: `(0.5, 0.5, 0.5, 0.5)`
- X90+Y180: `(0.7071, 0.7071, 0.0, 0.0)`

### 3. 物理稳定性
- 桌子和字母使用 `AssetBaseCfg`（静态装饰物，无刚体）
- 餐具在测试中禁用刚体避免碰撞弹飞
- 机器人使用 `ArticulationCfg`（带执行器的铰接体）

### 4. 保存场景
场景在运行1000步后自动保存为USD文件，可直接在Isaac Sim中打开查看。

---

## 环境要求

- **Isaac Sim**: 2023.1 或更高版本
- **Isaac Lab**: 0.54.3
- **Python**: 3.8+
- **依赖**: `pynput`（键盘控制）

```bash
pip install pynput
```

---

## 使用流程

### 快速开始
```bash
# 激活环境
conda activate isaaclab

# 运行完整场景 + 键盘控制
python scene_robot_keyboard.py
```

### 场景开发流程
1. **测试单个资源**: 使用 `test_table_letter.py` 或 `test_table_cutlery.py` 调试单个物体的位置、旋转、缩放
2. **组装场景**: 使用 `scene_11_tables.py` 组装多个物体
3. **添加机器人**: 使用 `scene_robot_tables.py` 或 `scene_robot_keyboard.py`
4. **保存场景**: 脚本会自动保存USD文件到 `assets/` 目录

---

## 故障排查

### 问题1: 物体弹飞
**原因**: 初始位置与其他物体发生碰撞
**解决**: 
- 提高初始Z坐标，让物体从高处下落
- 或使用 `AssetBaseCfg` 将物体设为静态（无物理）

### 问题2: 机器人前倾
**原因**: 机械臂初始姿态重心前倾
**解决**: 在 `initial_joint_pos` 中设置机械臂收起姿态

### 问题3: 键盘控制无响应
**原因**: 需要安装 `pynput` 库
**解决**: `pip install pynput`

### 问题4: 场景全黑
**原因**: 光照强度不足
**解决**: 增加 `DomeLightCfg` 的 `intensity` 参数，或添加额外的 `DistantLightCfg`

---

## 开发笔记

### 资源导入流程
1. 从Blender/CAD导出URDF
2. 使用Isaac Sim将URDF转换为USD
3. 在GUI中调整scale、rotation
4. 保存为 `*_edit.usd`
5. 在Python脚本中使用 `UsdFileCfg` 加载

### 场景组合策略
- 静态装饰物（桌子、字母）：使用 `AssetBaseCfg`
- 动态物体（餐具）：使用 `RigidObjectCfg` 或 `AssetBaseCfg`
- 机器人：使用 `ArticulationCfg` + `actuators`

---

## 参考资料

- [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab/)
- [Isaac Sim USD Reference](https://docs.omniverse.nvidia.com/isaacsim/latest/index.html)
- [pynput Documentation](https://pynput.readthedocs.io/)

---

## 作者

Ju Dong - 2026年3月

## 许可证

MIT License
