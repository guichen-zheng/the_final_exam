# models/

此目录用于存放YOLO模型文件(.pt格式)

## 默认模型

系统默认使用`yolov8n.pt`，首次运行时会自动下载。

## 支持的模型

- yolov8n.pt (推荐, 6MB, 最快)
- yolov8s.pt (22MB, 更准确)
- yolov8m.pt (52MB, 高精度)

## 使用自定义模型

1. 将模型文件放在此目录
2. 修改 `config/detector_params.yaml`:
   ```yaml
   model_path: "your_model.pt"
   ```
