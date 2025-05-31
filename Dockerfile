FROM nvidia/cuda:12.4-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG EXTRAS
ARG HF_PRECACHE_DIR
ARG HF_TKN_FILE

# Install system dependencies + Python + pip + cuDNN libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ffmpeg \
        git \
        libcudnn9 \
        libcudnn9-dev && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA 12.4 support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

COPY . .

# Install WhisperLiveKit directly, allowing for optional dependencies
RUN if [ -n "$EXTRAS" ]; then \
      echo "Installing with extras: [$EXTRAS]"; \
      pip install --no-cache-dir .[$EXTRAS]; \
    else \
      echo "Installing base package only"; \
      pip install --no-cache-dir .; \
    fi

# Enable in-container caching for Hugging Face models
VOLUME ["/root/.cache/huggingface/hub"]

# Conditionally copy cache and token if provided
RUN if [ -n "$HF_PRECACHE_DIR" ]; then \
      echo "Copying Hugging Face cache from $HF_PRECACHE_DIR"; \
      mkdir -p /root/.cache/huggingface/hub && \
      cp -r $HF_PRECACHE_DIR/* /root/.cache/huggingface/hub; \
    else \
      echo "No local Hugging Face cache specified, skipping copy"; \
    fi

RUN if [ -n "$HF_TKN_FILE" ]; then \
      echo "Copying Hugging Face token from $HF_TKN_FILE"; \
      mkdir -p /root/.cache/huggingface && \
      cp $HF_TKN_FILE /root/.cache/huggingface/token; \
    else \
      echo "No Hugging Face token file specified, skipping token setup"; \
    fi
    
# Expose port for the transcription server
EXPOSE 8000

# FIXED: Use direct Python file execution instead of problematic entry point script
ENTRYPOINT ["python3", "/app/whisperlivekit/basic_server.py"]
CMD ["--host", "0.0.0.0", "--model", "tiny.en"] 