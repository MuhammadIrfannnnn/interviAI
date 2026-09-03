import { useCallback, useEffect, useRef, useState } from "react";
import { audioService } from "../services/audioService";

/** Final outcome of a speak() call. */
export type SpeakResult =
  | "played"   // audio played through to the end
  | "blocked"  // browser blocked autoplay — audio loaded, waiting for a user click
  | "failed"   // TTS request or playback failed
  | "stopped"; // superseded by a newer speak()/stopSpeaking() call

const TTS_ERROR_MESSAGE =
  "Voice playback is unavailable. You can read the question and continue.";

interface UseSpeechOptions {
  /**
   * Fired when audio finishes playing naturally — including after a manual
   * replay once autoplay was unblocked. Not fired when playback is stopped
   * or superseded.
   */
  onPlaybackEnd?: () => void;
}

interface UseSpeechReturn {
  isSpeaking: boolean;
  isAutoplayBlocked: boolean;
  ttsError: string | null;
  /** Fetch TTS audio for the text and play it. Never rejects. */
  speak: (text: string) => Promise<SpeakResult>;
  /** Stop current playback and clean up. */
  stopSpeaking: () => void;
  /** Retry playback after the user interacts (call from a click handler). */
  retryAutoplay: () => void;
}

export function useSpeech(options: UseSpeechOptions = {}): UseSpeechReturn {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isAutoplayBlocked, setIsAutoplayBlocked] = useState(false);
  const [ttsError, setTtsError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const urlRef = useRef<string | null>(null);
  const resolveRef = useRef<((result: SpeakResult) => void) | null>(null);
  const onPlaybackEndRef = useRef(options.onPlaybackEnd);

  useEffect(() => {
    onPlaybackEndRef.current = options.onPlaybackEnd;
  }, [options.onPlaybackEnd]);

  const settle = useCallback((result: SpeakResult) => {
    const resolve = resolveRef.current;
    if (resolve) {
      resolveRef.current = null;
      resolve(result);
    }
  }, []);

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.onended = null;
      audioRef.current.onerror = null;
      audioRef.current = null;
    }
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    setIsSpeaking(false);
    setIsAutoplayBlocked(false);
  }, []);

  const stopSpeaking = useCallback(() => {
    cleanup();
    settle("stopped");
  }, [cleanup, settle]);

  const speak = useCallback(
    (text: string): Promise<SpeakResult> => {
      // Replace any current playback before starting new audio.
      cleanup();
      settle("stopped");
      setTtsError(null);

      return new Promise<SpeakResult>((resolve) => {
        resolveRef.current = resolve;

        audioService
          .speak(text)
          .then((blob) => {
            const url = URL.createObjectURL(blob);
            urlRef.current = url;

            const audio = new Audio(url);
            audioRef.current = audio;

            audio.onended = () => {
              setIsSpeaking(false);
              setIsAutoplayBlocked(false);
              settle("played");
              onPlaybackEndRef.current?.();
            };

            audio.onerror = () => {
              setIsSpeaking(false);
              setTtsError(TTS_ERROR_MESSAGE);
              settle("failed");
            };

            const playPromise = audio.play();
            if (playPromise !== undefined) {
              playPromise
                .then(() => {
                  setIsSpeaking(true);
                })
                .catch((err: DOMException) => {
                  if (err.name === "NotAllowedError") {
                    // Browser blocked autoplay — keep the audio element
                    // loaded so retryAutoplay() can start it on user click.
                    setIsAutoplayBlocked(true);
                    settle("blocked");
                  } else {
                    setIsSpeaking(false);
                    setTtsError(TTS_ERROR_MESSAGE);
                    settle("failed");
                  }
                });
            }
          })
          .catch(() => {
            setTtsError(TTS_ERROR_MESSAGE);
            settle("failed");
          });
      });
    },
    [cleanup, settle],
  );

  const retryAutoplay = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    setIsAutoplayBlocked(false);
    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          setIsSpeaking(true);
        })
        .catch(() => {
          setIsSpeaking(false);
          setTtsError(TTS_ERROR_MESSAGE);
          settle("failed");
        });
    }
  }, [settle]);

  // Cleanup on unmount — release audio element and object URL.
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.onended = null;
        audioRef.current.onerror = null;
        audioRef.current = null;
      }
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
        urlRef.current = null;
      }
    };
  }, []);

  return {
    isSpeaking,
    isAutoplayBlocked,
    ttsError,
    speak,
    stopSpeaking,
    retryAutoplay,
  };
}
