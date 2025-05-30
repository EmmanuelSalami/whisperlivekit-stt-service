# WhisperLiveKit STT Deployment Guide

This guide explains how to deploy WhisperLiveKit STT service to RunPod using GitHub Actions for automated Docker builds.

## 🚀 Quick Start

### Step 1: Setup GitHub Repository

1. **Fork or create a new repository** with this WhisperLiveKit code
2. **Set up Docker Hub secrets** in your GitHub repository:
   - Go to Repository Settings → Secrets and Variables → Actions
   - Add these secrets:
     - `DOCKER_USERNAME`: Your Docker Hub username
     - `DOCKER_TOKEN`: Your Docker Hub access token

### Step 2: Trigger Docker Build

1. **Push code to main branch** - This automatically triggers the GitHub Action
2. **Manual trigger**: Go to Actions tab → "Build and Push WhisperLiveKit Docker Image" → Run workflow
3. **Monitor build**: Check the Actions tab for build progress (~10-15 minutes)

### Step 3: Deploy to RunPod

1. **Update Docker image name** in `deploy_runpod.py`:
   ```python
   DOCKER_IMAGE = "your-dockerhub-username/whisperlivekit-stt:latest"
   ```

2. **Set RunPod API key**:
   ```powershell
   $env:RUNPOD_API_KEY = "your-runpod-api-key"
   ```

3. **Run deployment script**:
   ```bash
   python deploy_runpod.py
   ```

## 📋 What Gets Built

### Docker Image Contents
- **Base**: NVIDIA CUDA 12.8.1 with cuDNN runtime
- **Python**: 3.10 with WhisperLiveKit and dependencies
- **PyTorch**: CUDA 12.1 optimized build
- **Models**: Downloads Whisper models on first run
- **Server**: FastAPI + WebSocket endpoints on port 8000

### Exposed Endpoints
- **Web Interface**: `https://{pod-id}-8000.proxy.runpod.net/`
- **WebSocket STT**: `wss://{pod-id}-8000.proxy.runpod.net/asr`
- **Health Check**: `https://{pod-id}-8000.proxy.runpod.net/health`

## 🔧 Configuration Options

### WhisperLiveKit Server Options
Edit `deploy_runpod.py` DOCKER_COMMAND to customize:

```python
DOCKER_COMMAND = [
    "whisperlivekit-server",
    "--host", "0.0.0.0",
    "--port", "8000", 
    "--model", "base.en",      # Model size: tiny.en, base.en, small.en, medium.en, large
    "--language", "auto",      # Language detection: auto, en, es, fr, etc.
    "--diarization",          # Enable speaker diarization (optional)
    "--chunk-length", "30"     # Audio chunk length in seconds
]
```

### GPU Configuration
Available GPU types in `deploy_runpod.py`:
- `"NVIDIA RTX 4090"` - High performance (recommended for capacity testing)
- `"NVIDIA RTX 3090"` - Good performance
- `"NVIDIA A100"` - Enterprise grade

## 🧪 Testing the Deployment

### Automated Testing
The deployment script includes automatic testing:
```python
python deploy_runpod.py  # Deploys and tests automatically
```

### Manual Testing
1. **Web Interface**: Visit the pod URL in browser
2. **WebSocket**: Use JavaScript or Python WebSocket client
3. **Health Check**: `curl https://{pod-id}-8000.proxy.runpod.net/health`

### Example WebSocket Test
```python
import asyncio
import websockets
import json

async def test_stt():
    uri = "wss://{pod-id}-8000.proxy.runpod.net/asr"
    async with websockets.connect(uri) as websocket:
        # Send audio data
        with open("test_audio.wav", "rb") as f:
            audio_data = f.read()
            await websocket.send(audio_data)
        
        # Receive transcription
        response = await websocket.recv()
        print(f"Transcription: {json.loads(response)}")

asyncio.run(test_stt())
```

## 📊 Capacity Testing

### Load Testing Script
Create `load_test_stt.py` (similar to TTS load tester):
```python
# Test multiple concurrent WebSocket connections
# Measure response times and success rates
# Document RTX 4090 capacity limits
```

### Monitoring
- **Pod Logs**: Check RunPod console for errors
- **Response Times**: Monitor WebSocket latency
- **GPU Usage**: Use RunPod's GPU metrics dashboard
- **Success Rate**: Track successful transcriptions vs failures

## 🔄 Integration with LiveKit Agent

### After Successful Deployment
1. **Create STTService client class** (similar to TTS)
2. **Replace Deepgram calls** in monolithic app
3. **Test full conversation flow**: STT → LLM → TTS
4. **Load test complete pipeline**

## 🚨 Troubleshooting

### Build Failures
- **Check GitHub Actions logs** for specific errors
- **Verify Docker Hub credentials** in repository secrets
- **Ensure Dockerfile syntax** is correct

### Deployment Failures
- **Verify RunPod API key** is set correctly
- **Check Docker image exists** in Docker Hub
- **Monitor RunPod pod logs** for startup errors

### Runtime Issues
- **Check CUDA compatibility** (should work with RTX 4090)
- **Verify model downloads** in pod logs
- **Test with smaller models first** (tiny.en, base.en)

## 📈 Next Steps

1. **✅ Deploy successfully to RunPod**
2. **📊 Run capacity tests on RTX 4090**
3. **🔗 Integrate with LiveKit agent**
4. **🚀 Test full conversation pipeline**
5. **📋 Document performance characteristics** 