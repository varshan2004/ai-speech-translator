document.addEventListener("DOMContentLoaded", () => {

  /* =======================
     ELEMENT REFERENCES
  ======================= */
  const statusBox = document.getElementById("status");

  const audio = document.getElementById("audio");
  const video = document.getElementById("video");
  const subtitleOverlay = document.getElementById("subtitleOverlay");
  const downloadBtn = document.getElementById("downloadAudio");

  const originalText = document.getElementById("originalText");
  const translatedText = document.getElementById("translatedText");

  const language = document.getElementById("language");

  const audioInput = document.getElementById("audioInput");
  const videoInput = document.getElementById("videoInput");
  const urlInput = document.getElementById("urlInput");

  const audioBtn = document.getElementById("audioBtn");
  const videoBtn = document.getElementById("videoBtn");
  const urlBtn   = document.getElementById("urlBtn");

  const micStart = document.getElementById("micStart");
  const micStop  = document.getElementById("micStop");
  const micBtn   = document.getElementById("micBtn");
  const micStatus = document.getElementById("micStatus");

  const cards = {
    audio: document.getElementById("audioCard"),
    video: document.getElementById("videoCard"),
    mic:   document.getElementById("micCard"),
    url:   document.getElementById("urlCard")
  };

  /* =======================
     MODE SWITCHING
  ======================= */
  document.querySelectorAll(".mode").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".mode").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      Object.values(cards).forEach(c => c.classList.add("hidden"));
      cards[btn.dataset.mode].classList.remove("hidden");

      resetOutput();
    };
  });

  function resetOutput() {
    originalText.innerText = "";
    translatedText.innerText = "";
    audio.src = "";
    video.src = "";
    subtitleOverlay.innerText = "";
    downloadBtn.style.display = "none";
    statusBox.innerText = "Waiting for input…";
  }

  /* =======================
     VIDEO SUBTITLE SYNC
  ======================= */
  let videoCaptions = [];
  let videoSyncOffset = 0;

  function attachVideoSubtitles(captions) {
    videoCaptions = captions || [];

    if (videoCaptions.length > 0) {
      // align video time to first spoken word
      videoSyncOffset = videoCaptions[0].start;
    } else {
      videoSyncOffset = 0;
    }
  }

  video.ontimeupdate = () => {
    if (!videoCaptions.length) {
      subtitleOverlay.innerText = "";
      return;
    }

    const syncedTime = video.currentTime + videoSyncOffset;

    const active = videoCaptions.find(
      c => syncedTime >= c.start && syncedTime <= c.end
    );

    subtitleOverlay.innerText = active ? active.text : "";
  };

  /* =======================
     COMMON AUDIO HANDLER
  ======================= */
  function handleTranslatedAudio(data) {
    const audioUrl = `/api/audio/${data.audio_path}`;

    audio.src = audioUrl + `?t=${Date.now()}`;
    audio.play();

    downloadBtn.href = audioUrl;
    downloadBtn.download = data.audio_path;
    downloadBtn.style.display = "inline-block";
  }

  /* =======================
     AUDIO / VIDEO FILE
  ======================= */
  async function handleFile(file, isVideo) {
    if (!file) {
      alert("Please select a file");
      return;
    }

    statusBox.innerText = "Processing…";

    const fd = new FormData();
    fd.append("file", file);
    fd.append("target_lang", language.value);

    const res = await fetch("/api/translate/audio", {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    originalText.innerText = data.original_text;
    translatedText.innerText = data.translated_text;

    handleTranslatedAudio(data);

    if (isVideo) {
      video.src = URL.createObjectURL(file);
      video.load();
      attachVideoSubtitles(data.captions);
    }

    statusBox.innerText = "Done ✔";
  }

  audioBtn.onclick = () => handleFile(audioInput.files[0], false);
  videoBtn.onclick = () => handleFile(videoInput.files[0], true);

  /* =======================
     MICROPHONE
  ======================= */
  let recorder, micChunks = [], micBlob = null;

  micStart.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    micChunks = [];

    recorder.ondataavailable = e => micChunks.push(e.data);
    recorder.onstop = () => {
      micBlob = new Blob(micChunks, { type: "audio/wav" });
      micBtn.disabled = false;
      micStatus.innerText = "Recorded";
    };

    recorder.start();
    micStatus.innerText = "Recording…";
    micStop.disabled = false;
  };

  micStop.onclick = () => recorder.stop();

  micBtn.onclick = async () => {
    statusBox.innerText = "Translating mic…";

    const fd = new FormData();
    fd.append("audio", micBlob);
    fd.append("target_lang", language.value);

    const res = await fetch("/api/translate/mic", {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    originalText.innerText = data.original_text;
    translatedText.innerText = data.translated_text;

    handleTranslatedAudio(data);

    statusBox.innerText = "Mic done ✔";
  };

  /* =======================
     URL
  ======================= */
  urlBtn.onclick = async () => {
    if (!urlInput.value.trim()) {
      alert("Paste a URL");
      return;
    }

    statusBox.innerText = "Downloading & translating URL…";

    const res = await fetch("/api/translate/url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: urlInput.value,
        target_lang: language.value
      })
    });

    const data = await res.json();

    originalText.innerText = data.original_text;
    translatedText.innerText = data.translated_text;

    handleTranslatedAudio(data);

    statusBox.innerText = "URL done ✔";
  };

});
