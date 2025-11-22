# --- ベースイメージ ---
FROM python:3.13-slim

# --- 作業ディレクトリ ---
WORKDIR /app

# --- 必要なシステムパッケージ ---
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# --- Python依存関係 ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Botソースコード ---
COPY bot.py .

# --- 環境変数 ---
# Render側でDISCORD_TOKENをSecretに登録して使う
ENV DISCORD_TOKEN=${DISCORD_TOKEN}
ENV YDL_COOKIES_PATH=${YDL_COOKIES_PATH}  # 必要なら

# --- Bot起動 ---
CMD ["python", "bot.py"]
