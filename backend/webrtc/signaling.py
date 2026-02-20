import asyncio
import json
import websockets
from aiortc import RTCSessionDescription, RTCPeerConnection, RTCConfiguration, RTCIceServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebRTCSignaling:
    def __init__(self):
        self.peer_connections = {}
        
    async def handle_signaling(self, websocket, path):
        """Handle WebRTC signaling via WebSocket"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'offer':
                    await self.handle_offer(websocket, data)
                elif data['type'] == 'answer':
                    await self.handle_answer(data)
                elif data['type'] == 'ice-candidate':
                    await self.handle_ice_candidate(data)
                elif data['type'] == 'close':
                    await self.handle_close(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            
    async def handle_offer(self, websocket, data):
        """Handle incoming WebRTC offer"""
        peer_id = data['peer_id']
        
        # Create RTCPeerConnection
        pc = RTCPeerConnection()
        self.peer_connections[peer_id] = pc
        
        # Set remote description
        offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
        await pc.setRemoteDescription(offer)
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        # Send answer back
        response = {
            'type': 'answer',
            'peer_id': peer_id,
            'sdp': pc.localDescription.sdp
        }
        await websocket.send(json.dumps(response))
        
        # Handle ICE candidates
        @pc.on('icecandidate')
        async def on_icecandidate(candidate):
            if candidate:
                await websocket.send(json.dumps({
                    'type': 'ice-candidate',
                    'peer_id': peer_id,
                    'candidate': {
                        'candidate': candidate.candidate,
                        'sdpMid': candidate.sdpMid,
                        'sdpMLineIndex': candidate.sdpMLineIndex
                    }
                }))
                
    async def handle_answer(self, data):
        """Handle answer from client"""
        peer_id = data['peer_id']
        pc = self.peer_connections.get(peer_id)
        
        if pc:
            answer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
            await pc.setRemoteDescription(answer)
            
    async def handle_ice_candidate(self, data):
        """Handle ICE candidate from client"""
        peer_id = data['peer_id']
        pc = self.peer_connections.get(peer_id)
        
        if pc and data['candidate']:
            await pc.addIceCandidate(data['candidate'])
            
    async def handle_close(self, data):
        """Close peer connection"""
        peer_id = data['peer_id']
        if peer_id in self.peer_connections:
            await self.peer_connections[peer_id].close()
            del self.peer_connections[peer_id]