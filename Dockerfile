# --- ベースイメージ ---
FROM python:3.13-slim

# --- 作業ディレクトリ ---
WORKDIR /app

# --- 必要なシステムパッケージ ---
# ffmpeg とビルドに必要な最低限のパッケージを追加
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Python パッケージ ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Bot コードをコピー ---
COPY bot.py .

# --- 環境変数 (必要ならここにDISCORD_TOKENなどをセット可能) ---
# ENV DISCORD_TOKEN=your_token_here

# --- Bot 起動 ---
CMD ["python", "bot.py"]
