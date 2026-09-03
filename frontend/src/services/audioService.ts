import api from "./api";

/** Derive the file extension from the blob's actual MIME type. */
function extensionFor(mimeType: string): string {
  if (mimeType.includes("mp4")) return "mp4";
  if (mimeType.includes("ogg")) return "ogg";
  if (mimeType.includes("mpeg")) return "mp3";
  if (mimeType.includes("wav")) return "wav";
  return "webm"; // MediaRecorder default in Chrome/Firefox/Edge
}

export const audioService = {
  /**
   * Send a recorded audio Blob to the backend STT endpoint.
   * Returns the transcribed text.
   */
  async transcribe(blob: Blob): Promise<{ text: string }> {
    const form = new FormData();
    // The multipart part's Content-Type comes from the blob itself (e.g.
    // "audio/webm;codecs=opus"); the filename extension just has to match it.
    form.append("audio", blob, `recording.${extensionFor(blob.type)}`);
    const { data } = await api.post<{ text: string }>(
      "/audio/transcribe",
      form,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return data;
  },

  /**
   * Send text to the backend TTS endpoint.
   * Returns the audio Blob (mp3).
   */
  async speak(text: string): Promise<Blob> {
    const { data } = await api.post("/audio/speech", { text }, {
      responseType: "blob",
    });
    return data;
  },
};
