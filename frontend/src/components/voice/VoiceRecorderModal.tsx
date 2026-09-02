import React, { useState, useEffect, useRef } from 'react';
import { X, Mic, Square, RotateCcw, Save, AlertCircle, CheckCircle2 } from 'lucide-react';
import { VoiceExercise, VoiceSessionCreateRequest } from '../../types';
import { Button } from '../ui/Button';

interface VoiceRecorderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: VoiceSessionCreateRequest) => Promise<void>;
  selectedExercise?: VoiceExercise | null;
}

type RecorderStatus = 'idle' | 'recording' | 'recorded' | 'error';

export const VoiceRecorderModal: React.FC<VoiceRecorderModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  selectedExercise,
}) => {
  const [status, setStatus] = useState<RecorderStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const [repetitionCount, setRepetitionCount] = useState(1);
  const [parentNotes, setParentNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const cleanupStream = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    mediaRecorderRef.current = null;
  };

  const cleanupAudioUrl = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
  };

  useEffect(() => {
    if (!isOpen) {
      cleanupStream();
      cleanupAudioUrl();
      setStatus('idle');
      setElapsedSeconds(0);
      setErrorMessage(null);
      setRepetitionCount(1);
      setParentNotes('');
    }
    return () => {
      cleanupStream();
      cleanupAudioUrl();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const startRecording = async () => {
    try {
      setErrorMessage(null);
      cleanupAudioUrl();
      audioChunksRef.current = [];

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setStatus('error');
        setErrorMessage('Browser microphone recording is not supported in this environment.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setStatus('recorded');
      };

      mediaRecorder.start(250); // collect 250ms chunks
      setStatus('recording');
      setElapsedSeconds(0);

      timerIntervalRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      cleanupStream();
      setStatus('error');
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMessage('Microphone access was denied. Please allow microphone permissions in your browser.');
      } else {
        setErrorMessage('Failed to start microphone recording: ' + (err.message || 'Unknown error'));
      }
    }
  };

  const stopRecording = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleReset = () => {
    cleanupStream();
    cleanupAudioUrl();
    setStatus('idle');
    setElapsedSeconds(0);
    setErrorMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const duration = Math.max(1, elapsedSeconds);

    try {
      setIsSubmitting(true);
      const payload: VoiceSessionCreateRequest = {
        exercise_id: selectedExercise ? selectedExercise.id : undefined,
        duration_seconds: duration,
        repetition_count: repetitionCount,
        parent_notes: parentNotes.trim() || undefined,
        audio_s3_key: `local_session/${Date.now()}`,
      };
      await onSubmit(payload);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-lg rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {selectedExercise ? `Practice: ${selectedExercise.title}` : 'Voice Practice Session'}
              </h2>
              <p className="text-[11px] text-charcoal-600">
                Record practice time and observational notes locally.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 overflow-y-auto flex-1 text-xs">
          {/* Exercise Prompt Reminder if Selected */}
          {selectedExercise && (
            <div className="p-3 bg-ivory-50 border border-stone-200/80 rounded-2xl space-y-1">
              <span className="text-[10px] font-bold text-teal-900 uppercase">Target Prompt</span>
              <p className="text-xs text-charcoal-800 italic font-medium">
                "{selectedExercise.prompt_text}"
              </p>
            </div>
          )}

          {/* Recording Control Center */}
          <div className="p-5 bg-teal-50/60 rounded-3xl border border-teal-100 flex flex-col items-center justify-center gap-3 text-center">
            {status === 'idle' && (
              <>
                <button
                  type="button"
                  onClick={startRecording}
                  className="w-16 h-16 rounded-full bg-teal-900 text-white flex items-center justify-center shadow-warm-md hover:scale-105 active:scale-95 transition"
                  aria-label="Start Recording"
                >
                  <Mic className="w-7 h-7 text-coral-400" />
                </button>
                <div className="space-y-0.5">
                  <span className="font-heading font-bold text-sm text-teal-900 block">
                    Ready to Practice
                  </span>
                  <span className="text-[11px] text-charcoal-600">
                    Tap the microphone to start recording your practice session.
                  </span>
                </div>
              </>
            )}

            {status === 'recording' && (
              <>
                <div className="relative">
                  <div className="w-16 h-16 rounded-full bg-coral-500 text-white flex items-center justify-center animate-pulse shadow-warm-md">
                    <Square className="w-6 h-6" />
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="font-mono font-bold text-2xl text-teal-900">
                    {Math.floor(elapsedSeconds / 60)}:{(elapsedSeconds % 60).toString().padStart(2, '0')}
                  </span>
                  <p className="text-[11px] font-semibold text-coral-600">
                    Recording in progress...
                  </p>
                </div>

                <Button
                  type="button"
                  variant="primary"
                  size="sm"
                  onClick={stopRecording}
                  leftIcon={<Square className="w-3.5 h-3.5" />}
                >
                  Stop Recording
                </Button>
              </>
            )}

            {status === 'recorded' && (
              <div className="w-full space-y-3">
                <div className="flex items-center justify-center gap-2 text-sage-800">
                  <CheckCircle2 className="w-4 h-4 text-sage-700" />
                  <span className="font-bold text-xs">
                    Recording captured ({elapsedSeconds}s)
                  </span>
                </div>

                {audioUrl && (
                  <audio
                    src={audioUrl}
                    controls
                    className="w-full h-10 rounded-xl outline-none"
                  />
                )}

                <div className="flex items-center justify-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    leftIcon={<RotateCcw className="w-3 h-3" />}
                  >
                    Rerecord
                  </Button>
                </div>
              </div>
            )}

            {status === 'error' && (
              <div className="p-3 bg-white rounded-2xl border border-coral-200 text-coral-700 text-xs space-y-2 max-w-sm">
                <div className="flex items-center justify-center gap-1.5 font-bold">
                  <AlertCircle className="w-4 h-4" />
                  <span>Microphone Access Notice</span>
                </div>
                <p className="text-[11px] leading-relaxed text-charcoal-600">
                  {errorMessage || 'Unable to access microphone. You can still manually log your session duration below.'}
                </p>
                <Button type="button" variant="outline" size="sm" onClick={handleReset}>
                  Try Again
                </Button>
              </div>
            )}
          </div>

          {/* Session Details Form */}
          <div className="space-y-3 pt-2">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-charcoal-700 mb-1">
                  Duration (seconds) *
                </label>
                <input
                  type="number"
                  min="1"
                  max="3600"
                  required
                  value={elapsedSeconds || 30}
                  onChange={(e) => setElapsedSeconds(Number(e.target.value))}
                  className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
                />
              </div>

              <div>
                <label className="block font-bold text-charcoal-700 mb-1">
                  Repetitions Completed
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  required
                  value={repetitionCount}
                  onChange={(e) => setRepetitionCount(Number(e.target.value))}
                  className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
                />
              </div>
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Parent / Caregiver Observations (Optional)
              </label>
              <textarea
                rows={2}
                placeholder="e.g. Practiced 3 times while looking in mirror, smiled and attempted /pa/ sound..."
                value={parentNotes}
                onChange={(e) => setParentNotes(e.target.value)}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 resize-none"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="submit"
              isLoading={isSubmitting}
              leftIcon={<Save className="w-3.5 h-3.5" />}
            >
              Save Practice Session
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
