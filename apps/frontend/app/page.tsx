'use client';

import { useEffect, useState, useRef } from 'react';
import {
  Room,
  RoomEvent,
  createLocalVideoTrack,
  RemoteTrack,
  RemoteTrackPublication,
  RemoteParticipant,
} from 'livekit-client';
import {
  LuCameraOff,
  LuMicOff,
  LuLogOut,
  LuMic,
  LuCamera,
} from 'react-icons/lu';

const BACKEND_URL = 'http://localhost:8000';

export default function App() {
  const [participantName, setParticipantName] = useState<string>('');
  const [room, setRoom] = useState<Room | null>(null);
  const [isJoined, setIsJoined] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isMicOn, setIsMicOn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const localVideoRef = useRef<HTMLVideoElement | null>(null);
  const remoteVideoRef = useRef<HTMLVideoElement | null>(null);

  const joinRoom = async () => {
    if (!participantName) {
      setError('Please enter your name.');
      return;
    }
    setError(null);

    try {
      const response = await fetch(
        `${BACKEND_URL}/token?roomName=test-room&participantName=${encodeURIComponent(
          participantName,
        )}`,
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { token: string; livekit_url: string } = await response.json();
      const { token, livekit_url } = data;

      const livekitRoom = new Room();
      await livekitRoom.connect(livekit_url, token);
      setRoom(livekitRoom);
      setIsJoined(true);

      console.log('Connected to room:', livekitRoom.name);

      // Handle remote participant video tracks
      livekitRoom.on(
        RoomEvent.TrackSubscribed,
        (
          track: RemoteTrack,
          _publication: RemoteTrackPublication,
          _participant: RemoteParticipant,
        ) => {
          if (track.kind === 'video' && remoteVideoRef.current) {
            track.attach(remoteVideoRef.current);
          }
        },
      );
    } catch (err) {
      console.error('Error joining room:', err);
      setError(
        'Failed to join the room. Please check your backend and network connection.',
      );
    }
  };

  const leaveRoom = () => {
    if (!room) return;

    room.disconnect();
    setRoom(null);
    setIsJoined(false);
    setIsCameraOn(false);
    setIsMicOn(false);

    if (localVideoRef.current) localVideoRef.current.srcObject = null;
    if (remoteVideoRef.current) remoteVideoRef.current.srcObject = null;
  };

  const toggleCamera = async () => {
    if (!room) return;
    try {
      if (isCameraOn) {
        room.localParticipant.getTrackPublications().forEach((pub) => {
          if (pub.kind === 'video' && pub.track) {
            const localPub = pub as import('livekit-client').LocalTrackPublication;
            room.localParticipant.unpublishTrack(localPub.track!); // <-- non-null assertion
            localPub.track!.stop();
          }
        });
        
        
      } else {
        const videoTrack = await createLocalVideoTrack();
        await room.localParticipant.publishTrack(videoTrack);
        if (localVideoRef.current) videoTrack.attach(localVideoRef.current);
      }
      
      setIsCameraOn((prev) => !prev);
    } catch (err) {
      console.error('Error toggling camera:', err);
      setError('Failed to toggle camera. Please check your permissions.');
    }
  };

  const toggleMicrophone = async () => {
    if (!room) return;
    try {
      await room.localParticipant.setMicrophoneEnabled(!isMicOn);
      setIsMicOn((prev) => !prev);
    } catch (err) {
      console.error('Error toggling microphone:', err);
      setError('Failed to toggle microphone. Please check your permissions.');
    }
  };

  useEffect(() => {
    return () => {
      if (room) room.disconnect();
    };
  }, [room]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-8 bg-gray-100 p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-2xl">
        <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-6">
          LiveKit Video Call
        </h1>

        {error && (
          <div
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative mb-4"
            role="alert"
          >
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {!isJoined ? (
          <div className="flex flex-col items-center">
            <input
              type="text"
              placeholder="Enter your name"
              className="w-full border-2 border-gray-300 rounded-lg p-3 text-lg mb-4 focus:outline-none focus:border-blue-500 transition-colors"
              value={participantName}
              onChange={(e) => setParticipantName(e.target.value)}
            />
            <button
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg text-lg transition-colors duration-200"
              onClick={joinRoom}
            >
              Join Room
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <p className="text-xl text-center text-gray-600 mb-4">
              You are in the room as:{' '}
              <span className="font-semibold text-gray-800">
                {participantName}
              </span>
            </p>
            <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden shadow-md">
                <video
                  ref={localVideoRef}
                  className="w-full h-full object-cover"
                  autoPlay
                  playsInline
                  muted
                />
                <div className="absolute bottom-2 left-2 bg-gray-800 text-white text-xs px-2 py-1 rounded-full">
                  You
                </div>
              </div>
              <div className="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden shadow-md">
                <video
                  ref={remoteVideoRef}
                  className="w-full h-full object-cover"
                  autoPlay
                  playsInline
                />
                <div className="absolute bottom-2 left-2 bg-gray-800 text-white text-xs px-2 py-1 rounded-full">
                  Remote Participant
                </div>
              </div>
            </div>
            <div className="flex justify-center items-center mt-6 space-x-4">
              <button
                className={`flex items-center justify-center p-3 rounded-full shadow-lg transition-all duration-200 ${
                  isCameraOn
                    ? 'bg-red-500 hover:bg-red-600'
                    : 'bg-gray-600 hover:bg-gray-700'
                } text-white`}
                onClick={toggleCamera}
              >
                {isCameraOn ? <LuCameraOff size={24} /> : <LuCamera size={24} />}
              </button>
              <button
                className={`flex items-center justify-center p-3 rounded-full shadow-lg transition-all duration-200 ${
                  isMicOn
                    ? 'bg-red-500 hover:bg-red-600'
                    : 'bg-gray-600 hover:bg-gray-700'
                } text-white`}
                onClick={toggleMicrophone}
              >
                {isMicOn ? <LuMicOff size={24} /> : <LuMic size={24} />}
              </button>
              <button
                className="flex items-center justify-center p-3 rounded-full shadow-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors duration-200"
                onClick={leaveRoom}
              >
                <LuLogOut size={24} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
