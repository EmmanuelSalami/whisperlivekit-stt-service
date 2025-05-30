#!/usr/bin/env python3
"""
RunPod Deployment Script for WhisperLiveKit STT Service
Deploys the containerized STT service to RunPod with RTX 4090 GPU support
"""

import runpod
import os
import json
from datetime import datetime

# Configuration
DOCKER_IMAGE = "ghcr.io/emmanuelsalami/whisperlivekit-stt-service:latest"  # Updated to actual GitHub Container Registry image
POD_TYPE = "NVIDIA GeForce RTX 5090"  # Latest GPU with CUDA 12.8+ support
CONTAINER_DISK_GB = 20  # Enough for models and logs
VOLUME_MOUNT_PATH = "/runpod-volume"

# Environment variables for the container
CONTAINER_ENV = {
    "PYTHONUNBUFFERED": "1",
    "HF_HOME": "/runpod-volume/.cache/huggingface"  # Cache models on volume
}

# Docker run command for WhisperLiveKit
DOCKER_COMMAND = [
    "whisperlivekit-server",
    "--host", "0.0.0.0",
    "--port", "8000", 
    "--model", "base.en",  # Start with base model for testing
    "--language", "auto"
]

def create_runpod_deployment():
    """Create and deploy WhisperLiveKit STT service on RunPod"""
    
    # Ensure API key is set
    api_key = os.getenv('RUNPOD_API_KEY')
    if not api_key:
        print("❌ Error: RUNPOD_API_KEY environment variable not set")
        print("Set it with: $env:RUNPOD_API_KEY='your-api-key'")
        return None
    
    runpod.api_key = api_key
    
    print("🚀 Deploying WhisperLiveKit STT to RunPod...")
    print(f"📦 Docker Image: {DOCKER_IMAGE}")
    print(f"🎯 GPU Type: {POD_TYPE}")
    print(f"💾 Container Disk: {CONTAINER_DISK_GB}GB")
    
    try:
        # Create the pod
        pod = runpod.create_pod(
            name=f"whisper-stt-{datetime.now().strftime('%m%d-%H%M')}",
            image_name=DOCKER_IMAGE,
            gpu_type_id=POD_TYPE,
            container_disk_in_gb=CONTAINER_DISK_GB,
            volume_mount_path=VOLUME_MOUNT_PATH,
            ports="8000/http",
            env=CONTAINER_ENV,
            docker_args=" ".join(DOCKER_COMMAND)
        )
        
        pod_id = pod.get('id')
        if pod_id:
            print(f"✅ Pod created successfully!")
            print(f"📋 Pod ID: {pod_id}")
            print(f"🌐 Access URL: https://{pod_id}-8000.proxy.runpod.net")
            print(f"🔗 WebSocket URL: wss://{pod_id}-8000.proxy.runpod.net/asr")
            
            # Save pod info for later use
            pod_info = {
                "pod_id": pod_id,
                "created_at": datetime.now().isoformat(),
                "docker_image": DOCKER_IMAGE,
                "access_url": f"https://{pod_id}-8000.proxy.runpod.net",
                "websocket_url": f"wss://{pod_id}-8000.proxy.runpod.net/asr",
                "model": "base.en"
            }
            
            with open("runpod_stt_pod_info.json", "w") as f:
                json.dump(pod_info, f, indent=2)
            
            print("💾 Pod information saved to runpod_stt_pod_info.json")
            return pod_info
        else:
            print("❌ Failed to create pod")
            print(f"Response: {pod}")
            return None
            
    except Exception as e:
        print(f"❌ Error deploying to RunPod: {e}")
        return None

def test_deployment(pod_info):
    """Test the deployed STT service"""
    import requests
    import time
    
    if not pod_info:
        print("❌ No pod info available for testing")
        return
    
    access_url = pod_info["access_url"]
    print(f"🧪 Testing deployment at {access_url}")
    
    # Wait for pod to be ready
    print("⏳ Waiting for pod to be ready...")
    for i in range(180):  # Wait up to 30 minutes (was 5 minutes)
        try:
            response = requests.get(f"{access_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ STT service is responding!")
                print(f"📊 Status Code: {response.status_code}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(10)
        print(f"⏳ Still waiting... ({i+1}/180)")
    
    print("❌ Pod failed to respond within 30 minutes")
    return False

if __name__ == "__main__":
    print("🎙️ WhisperLiveKit STT RunPod Deployment")
    print("=" * 50)
    
    # Deploy the pod
    pod_info = create_runpod_deployment()
    
    # Test the deployment
    if pod_info:
        print("\n" + "=" * 50)
        test_deployment(pod_info) 