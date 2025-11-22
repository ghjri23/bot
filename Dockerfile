# ベースイメージ
FROM python:3.13-slim

# ffmpeg をインストール
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# 依存関係をコピー
COPY requirements.txt .

# ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Bot のコードをコピー
COPY . .

# Bot を起動
CMD ["python", "bot.py"]
