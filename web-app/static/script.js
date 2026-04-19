let mediaRecorder;
let audioChunks = [];
let timerInterval;
let seconds = 0;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptionText = document.getElementById('transcriptionText');
const recordingTime = document.getElementById('recordingTime');

function setTranscriptionStatus(message, isError = false) {
    if (!transcriptionText) {
        return;
    }

    transcriptionText.innerHTML = isError
        ? `<p class="error">${message}</p>`
        : `<p class="status">${message}</p>`;
}

function updateTimerDisplay() {
    if (!recordingTime) {
        return;
    }

    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    recordingTime.textContent = `${mins}:${secs}`;
}

function startTimer() {
    clearInterval(timerInterval);
    seconds = 0;
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        seconds += 1;
        updateTimerDisplay();
    }, 1000);
}

// //called when start recording button is pressed
async function startRecording() {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    // triggers audio upload on recording stop
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await uploadAudio(audioBlob);
    };

    mediaRecorder.start();
    
    if (startBtn) {
        startBtn.disabled = true;
    }
    if (stopBtn) {
        stopBtn.disabled = false;
    }

    startTimer();
    setTranscriptionStatus('Recording in progress...');
}

// called when stop recording button is pressed
function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        return;
    }

    mediaRecorder.stop();
    clearInterval(timerInterval);
    if (startBtn) {
        startBtn.disabled = false;
    }
    if (stopBtn) {
        stopBtn.disabled = true;
    }
}

// attempts to send audio file to web app api
async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio_file', blob, 'lecture.wav');
    setTranscriptionStatus('ML Client is analyzing audio...');

    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json(); 
            localStorage.setItem('currentNoteId', data.note_id);
            window.location.reload();
        } else {
            setTranscriptionStatus('Analysis failed.', true);
        }
    } catch (err) {
        console.error(err);
        setTranscriptionStatus('Connection Error.', true);
    }
}

