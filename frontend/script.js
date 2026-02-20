// WebRTC and WebSocket configuration
let localStream = null;
let remoteStream = null;
let peerConnection = null;
let websocket = null;
let mediaRecorder = null;
let recordedChunks = [];

const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

// DOM elements
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const statusText = document.getElementById('statusText');
const recognizedText = document.getElementById('recognizedText');
const llmResponse = document.getElementById('llmResponse');
const debugInfo = document.getElementById('debugInfo');

// Initialize WebSocket connection
function initWebSocket() {
    websocket = new WebSocket('ws://localhost:8765');
    
    websocket.onopen = () => {
        updateStatus('Connected to server');
        logDebug('WebSocket connected');
    };
    
    websocket.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        logDebug('Received: ' + JSON.stringify(data));
        
        switch(data.type) {
            case 'text':
                recognizedText.textContent = data.text;
                // Send to LLM (external)
                await sendToLLM(data.text);
                break;
                
            case 'video':
                // Display received video
                const videoBlob = new Blob([new Uint8Array(data.video)], {type: 'video/mp4'});
                const videoUrl = URL.createObjectURL(videoBlob);
                remoteVideo.src = videoUrl;
                remoteVideo.play();
                logDebug('Video received: ' + data.path);
                break;
                
            case 'answer':
                await handleAnswer(data);
                break;
                
            case 'ice-candidate':
                await handleIceCandidate(data);
                break;
        }
    };
    
    websocket.onclose = () => {
        updateStatus('Disconnected from server');
        logDebug('WebSocket disconnected');
    };
    
    websocket.onerror = (error) => {
        logDebug('WebSocket error: ' + JSON.stringify(error));
    };
}

// Get user media
async function startCall() {
    try {
        updateStatus('Requesting camera and microphone...');
        
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        
        localVideo.srcObject = localStream;
        
        // Initialize WebRTC
        await initializeWebRTC();
        
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        
        updateStatus('Connected - Ready to communicate');
        
    } catch (error) {
        logDebug('Error: ' + error.message);
        updateStatus('Error accessing media devices');
    }
}

// Initialize WebRTC
async function initializeWebRTC() {
    peerConnection = new RTCPeerConnection(configuration);
    
    // Add local stream to peer connection
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
        if (!remoteStream) {
            remoteStream = new MediaStream();
            remoteVideo.srcObject = remoteStream;
        }
        remoteStream.addTrack(event.track);
    };
    
    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            websocket.send(JSON.stringify({
                type: 'ice-candidate',
                peer_id: 'user1',
                candidate: event.candidate
            }));
        }
    };
    
    // Create and send offer
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    
    websocket.send(JSON.stringify({
        type: 'offer',
        peer_id: 'user1',
        sdp: peerConnection.localDescription.sdp
    }));
}

// Handle WebRTC answer
async function handleAnswer(data) {
    const answer = new RTCSessionDescription({
        type: 'answer',
        sdp: data.sdp
    });
    await peerConnection.setRemoteDescription(answer);
}

// Handle ICE candidate
async function handleIceCandidate(data) {
    try {
        await peerConnection.addIceCandidate(data.candidate);
    } catch (error) {
        logDebug('Error adding ICE candidate: ' + error.message);
    }
}

// Stop call
function stopCall() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
        localVideo.srcObject = null;
    }
    
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    if (websocket) {
        websocket.send(JSON.stringify({
            type: 'close',
            peer_id: 'user1'
        }));
    }
    
    remoteVideo.srcObject = null;
    
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    
    updateStatus('Disconnected');
}

// Send audio to server for processing
async function sendAudioToServer(audioBlob) {
    const reader = new FileReader();
    reader.readAsArrayBuffer(audioBlob);
    reader.onloadend = () => {
        const audioData = new Uint8Array(reader.result);
        websocket.send(JSON.stringify({
            type: 'audio',
            audio: Array.from(audioData)
        }));
    };
}

// Send text to external LLM
async function sendToLLM(text) {
    try {
        updateStatus('Sending to LLM...');
        
        // This is where you'd call your external LLM
        // For demo, we'll simulate with a timeout
        setTimeout(async () => {
            const mockResponse = "नमस्ते, मैं आपका AI अवतार हूँ। कैसे मदद कर सकता हूँ?";
            llmResponse.textContent = mockResponse;
            
            // Send LLM response back to server for avatar generation
            websocket.send(JSON.stringify({
                type: 'llm_response',
                text: mockResponse
            }));
            
            updateStatus('Avatar response generated');
        }, 2000);
        
    } catch (error) {
        logDebug('LLM error: ' + error.message);
    }
}

// Toggle recording
function toggleRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        startRecording();
    } else {
        stopRecording();
    }
}

function startRecording() {
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(localStream);
    
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };
    
    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, {type: 'audio/webm'});
        sendAudioToServer(blob);
        document.getElementById('recordBtn').textContent = 'Start Recording';
    };
    
    mediaRecorder.start();
    document.getElementById('recordBtn').textContent = 'Stop Recording';
    logDebug('Recording started');
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        logDebug('Recording stopped');
    }
}

// Helper functions
function updateStatus(status) {
    statusText.textContent = status;
}

function logDebug(message) {
    const timestamp = new Date().toLocaleTimeString();
    debugInfo.textContent += `[${timestamp}] ${message}\n`;
    debugInfo.scrollTop = debugInfo.scrollHeight;
}

// Initialize on page load
window.onload = () => {
    initWebSocket();
    logDebug('Page loaded, WebSocket initialized');
};

// Cleanup on page unload
window.onbeforeunload = () => {
    if (websocket) {
        websocket.close();
    }
};