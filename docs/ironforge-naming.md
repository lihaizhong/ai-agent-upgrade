# IronForge 仓库命名规范

根据 Transformers 角色特性和项目类型，整理的仓库命名指南。

## 命名格式

```
ironforge-{role}-{type}
```

- `ironforge` - 前缀，表示金刚锻造生态
- `role` - 变形金刚角色名
- `type` - 项目类型

---

## 项目分类与命名

### 小程序

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Bumblebee | `ironforge-bumblebee-mini` | 敏捷、适应性强，适合体积敏感的小程序 |
| Bluestreak | `ironforge-bluestreak-mini` | 快速原型，快速上线迭代 |

### Web

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Jazz | `ironforge-jazz-web` | 优雅、有节奏感，Web 注重交互体验 |
| Sideswipe | `ironforge-sideswipe-web` | 灵活、侧面切入，Web 组件化开发 |

### H5

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Cliffjumper | `ironforge-cliffjumper-h5` | 跳跃、灵活适配，H5 需要多端适配 |
| Windcharger | `ironforge-windcharger-h5` | 快速充能，快速开发上线 |

### 后端

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Optimus Prime | `ironforge-optimus-api` | 领袖、核心 API 服务 |
| Ironhide | `ironforge-ironhide-core` | 重装硬汉，核心业务逻辑 |
| Shockwave | `ironforge-shockwave-service` | 冲击波，业务处理服务 |

### 全栈

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Sentinel | `ironforge-sentinel-fullstack` | 哨兵，全栈守卫 |
| Prowl | `ironforge-prowl-fullstack` | 潜行，前后端贯通 |

### SDK

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Wheeljack | `ironforge-wheeljack-sdk` | 工程师，工具属性强 |
| Perceptor | `ironforge-perceptor-lib` | 感知器，通用库/工具 |

### 基础设施

| 角色 | 仓库名 | 解释 |
|------|--------|------|
| Barricade | `ironforge-barricade-auth` | 路障，安全鉴权 |
| Soundwave | `ironforge-soundwave-metrics` | 声波，信息收集/监控 |
| Frenzy | `ironforge-frenzy-cicd` | 混乱，CI/CD 自动化 |

---

## 角色选择建议

- **小程序**：体积敏感，选择轻量角色
- **Web**：交互优先，选择灵活角色
- **H5**：多端适配，选择敏捷角色
- **后端**：业务核心，选择重量角色
- **全栈**：前后端贯通，选择平衡角色
- **SDK**：工具属性，选择工程角色
- **基础设施**：运维安全，选择守卫角色