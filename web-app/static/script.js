let mediaRecorder;
let audioChunks = [];
let timerInterval;
let seconds = 0;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptionText = document.getElementById('transcriptionText');
const recordingTime = document.getElementById('recordingTime');

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
    
    startBtn.disabled = true;
    stopBtn.disabled = false;
    startTimer();
    transcriptionText.innerHTML = '<p class="status">Recording in progress...</p>';
}

// called when stop recording button is pressed
function stopRecording() {
    mediaRecorder.stop();
    clearInterval(timerInterval);
    startBtn.disabled = false;
    stopBtn.disabled = true;
}

// attempts to send audio file to web app api
async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio_file', blob, 'lecture.wav');
    transcriptionText.innerHTML = '<p class="status">ML Client is analyzing audio...</p>';

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
            transcriptionText.innerHTML = '<p class="error">Analysis failed.</p>';
        }
    } catch (err) {
        console.error(err);
        transcriptionText.innerHTML = '<p class="error">Connection Error.</p>';
    }
}

async function generateSummary() {
    const summaryDisplay = document.getElementById('summaryDisplay');
    const summaryLoading = document.getElementById('summaryLoading');
    const summaryActions = document.getElementById('summaryActions');

    const noteId = localStorage.getItem('currentNoteId');
    if (!noteId) {
        alert('Record something first!');
        return;
    }

    summaryLoading.style.display = 'block';
    summaryDisplay.style.display = 'none';

    try {
        const response = await fetch(`/summarize/${noteId}`, {
            method: 'POST'
        });
        const data = await response.json();

        summaryDisplay.innerHTML = `<p>${data.summary}</p>`;
        summaryDisplay.style.display = 'block';
        summaryLoading.style.display = 'none';
        summaryActions.style.display = 'flex';
    } catch (error) {
        summaryDisplay.innerHTML = '<p>Error generating summary</p>';
        summaryDisplay.style.display = 'block';
        summaryLoading.style.display = 'none';
    }
}
