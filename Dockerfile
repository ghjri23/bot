# ベースイメージに Python と ffmpeg を含む
FROM python:3.12-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt .
COPY bot.py .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# Bot トークンを環境変数で渡す想定
ENV DISCORD_TOKEN="YOUR_BOT_TOKEN"

# Bot を起動
CMD ["python", "bot.py"]