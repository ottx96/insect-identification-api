# Insect Identification API

A Flask-based REST API for insect identification using computer vision and machine learning.

## Features

- REST API endpoint for insect identification
- Base64 image processing
- Integration with GBIF.org for species information
- Confidence threshold validation
- Comprehensive error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Usage

### POST /api/v1/identify

Identify insects in a base64-encoded image.

**Request Body:**
```json
{
  "custom_id": "sdgbwkng23kwegjb",
  "image_base64": "<base64 encoded image>"
}
```

**Success Response (200):**
```json
{
  "custom_id": "sdgbwkng23kwegjb",
  "identified_insects": [
    {
      "probability": 0.85,
      "latin_name": "Apis mellifera",
      "gbif_id": 1340286
    }
  ],
  "status_message": "Success"
}
```

**Error Response (400):**
```json
{
  "error": "Low confidence identification",
  "status_message": "Low confidence identification"
}
```

## Testing

Use the provided test script:
```bash
python test_api.py
```

# 特性
- 支持 2037 类 (可能是目, 科, 属或种等) 昆虫或其他节肢动物
- 模型开源, 持续更新.

# 安装
先安装 Anaconda, 然后执行
```
git clone https://github.com/quarrying/quarrying-insect-id.git
cd quarrying-insect-id
conda create -n insectid python=3.8 -y
conda activate insectid
pip install -r requirements.txt
```

# 用法 

参考 [demo.py](<demo.py>), 也可以在我的个人网站 (<https://www.quarryman.cn/insect>) 体验识别效果.


# ChangeLog

- 20211204 更新识别模型, 支持 2037 个昆虫分类单元, top1/top5 准确率为 0.922/0.981.
- 20211125 更新检测模型.
- 20211018 更新检测模型.
- 20211011 更新检测模型.
- 20211009 更新识别模型, 支持 1702 个昆虫分类单元, top1/top5 准确率为 0.915/0.973.
- 20210920 更新识别模型, 支持 1534 个昆虫分类单元.
- 20210908 更新识别模型, 支持 1372 个昆虫分类单元.
- 20210825 更新识别模型, 支持 1234 个昆虫分类单元.
- 20210815 更新识别模型, 支持 1068 个昆虫分类单元.
- 20210801 更新识别模型, 支持 868 个昆虫分类单元.
- 20210713 更新检测模型.
- 20210712 更新识别模型, 支持 840 个昆虫分类单元.
- 20210704 更新识别模型, 支持 820 个昆虫分类单元.
- 20210701 发布第一版模型, 支持 786 个昆虫分类单元.
