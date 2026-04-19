let mediaRecorder;
let audioChunks = [];
let timerInterval;
let seconds = 0;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptionText = document.getElementById('transcriptionText');
const recordingTime = document.getElementById('recordingTime');
const summaryDisplay = document.getElementById('summaryDisplay');
const summaryLoading = document.getElementById('summaryLoading');
const summaryActions = document.getElementById('summaryActions');
const notesList = document.getElementById('notesList');

let notes = [];

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
    recordingTime.textContent = '00:00';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (startBtn) {
        startBtn.disabled = false;
    }
    if (stopBtn) {
        stopBtn.disabled = true;
    }
}

// timer functionality
function startTimer() {
    seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        recordingTime.textContent = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }, 1000);
}

// past notes
function renderNotes(notesToRender = null) {
    const displayNotes = notesToRender || notes;
    
    if (displayNotes.length === 0) {
        notesList.innerHTML = '<div class="empty-state"><p>No notes found. Start recording to create your first note!</p></div>';
        return;
    }
    
    notesList.innerHTML = displayNotes.map(note => `
        <div class="note-item">
            <div class="note-header">
                <span class="note-time">${note.timestamp}</span>
                <button class="note-delete-btn" onclick="deleteNote(${note.id})" title="Delete note">✕</button>
            </div>
            <div class="note-text">${escapeHtml(note.text)}</div>
        </div>
    `).join('');
}

function displayPastNotes(filterTime = null) {
    // load notes from localStorage
    loadNotes();
    
    if (notes.length === 0) {
        notesList.innerHTML = '<div class="empty-state"><p>No past notes. Start recording to create your first note!</p></div>';
        return;
    }
    
    // filter by time
    let filteredNotes = notes;
    if (filterTime) {
        filteredNotes = filterNotesByTime(notes, filterTime);
    }
    
    renderNotes(filteredNotes);
}

function filterNotesByTime(notesArray, timeFilter) {
    // timeFilter options: 'today', 'week', 'month', 'all'
    const now = new Date();
    
    return notesArray.filter(note => {
        // timestamps tbd
        return true;
    });
}

function searchNotes(searchTerm) {
    loadNotes();
    
    if (!searchTerm) {
        renderNotes();
        return;
    }
    
    const filtered = notes.filter(note => 
        note.text.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    renderNotes(filtered);
}

function sortNotes(sortBy) {
    // sortBy options: 'recent', 'oldest', 'alphabetical'
    
    let sorted = [...notes];
    
    switch(sortBy) {
        case 'recent':
            sorted.sort((a, b) => b.id - a.id);
            break;
        case 'oldest':
            sorted.sort((a, b) => a.id - b.id);
            break;
        case 'alphabetical':
            sorted.sort((a, b) => a.text.localeCompare(b.text));
            break;
    }
    
    renderNotes(sorted);
}

function loadNotes() {
    const stored = localStorage.getItem('lectureNotes');
    notes = stored ? JSON.parse(stored) : [];
}

function saveNotes() {
    localStorage.setItem('lectureNotes', JSON.stringify(notes));
}

async function deleteNote(noteId) {
    const response = await fetch(`/notes/delete/${noteId}`, { method: 'POST' });
    if (response.ok) {
        window.location.reload();
    } else {
        alert('Failed to delete note.');
    }
}

async function deleteAllNotes() {
    const noteCards = document.querySelectorAll('.note-card');
    if (noteCards.length === 0) {
        alert('No notes to delete!');
        return;
    }

    if (confirm('Are you sure you want to delete all notes? This cannot be undone.')) {
        const response = await fetch('/notes/delete-all', { method: 'POST' });
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete notes.');
        }
    }
}

function exportNotes() {
    const noteCards = document.querySelectorAll('.note-card');
    if (noteCards.length === 0) {
        alert('No notes to export!');
        return;
    }

    const content = Array.from(noteCards).map(card => {
        const time = card.querySelector('.note-meta')?.textContent || '';
        const transcript = card.querySelectorAll('p')[0]?.textContent || '';
        const summary = card.querySelectorAll('p')[1]?.textContent || '';
        return `[${time}]\nTranscript: ${transcript}\nSummary: ${summary}`;
    }).join('\n---\n\n');

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', `lecture-notes-${new Date().toISOString().split('T')[0]}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// attempts to send audio file to web app api
async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio_file', blob, 'lecture.wav');
    setTranscriptionStatus('ML Client is analyzing audio...');

    // summary loading state
    summaryLoading.style.display = 'flex';
    summaryDisplay.style.display = 'none';
    summaryActions.style.display = 'none';

    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('currentNoteId', data.note_id);
            displayTranscript(data.transcript);
            sessionStorage.setItem('pendingSummary', data.summary);
            window.location.reload();
        } else {
            transcriptionText.innerHTML = '<p class="error">Analysis failed.</p>';
            summaryLoading.style.display = 'none';
        }
    } catch (err) {
        console.error(err);
        transcriptionText.innerHTML = '<p class="error">Connection Error.</p>';
        summaryLoading.style.display = 'none';
    }
}

// live transcript
function displayTranscript(transcript) {
    if (transcript) {
        transcriptionText.innerHTML = `<p>${escapeHtml(transcript)}</p>`;
    } else {
        transcriptionText.innerHTML = '<p class="error">No transcript available</p>';
    }
}

function addNoteToList(transcript) {
    const note = {
        id: Date.now(),
        text: transcript,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    notes.unshift(note);
    saveNotes();
    renderNotes();
}

// Summary

// async function generateSummary() {
//     const summaryDisplay = document.getElementById('summaryDisplay');
//     const summaryLoading = document.getElementById('summaryLoading');
//     const summaryActions = document.getElementById('summaryActions');

//     const noteId = localStorage.getItem('currentNoteId');
//     if (!noteId) {
//         alert('Record something first!');
//         return;
//     }

//     summaryLoading.style.display = 'block';
//     summaryDisplay.style.display = 'none';

//     try {
//         const response = await fetch(`/summarize/${noteId}`, {
//             method: 'POST'
//         });
//         const data = await response.json();

//         summaryDisplay.innerHTML = `<p>${data.summary}</p>`;
//         summaryDisplay.style.display = 'block';
//         summaryLoading.style.display = 'none';
//         summaryActions.style.display = 'flex';
//     } catch (error) {
//         summaryDisplay.innerHTML = '<p>Error generating summary</p>';
//         summaryDisplay.style.display = 'block';
//         summaryLoading.style.display = 'none';
//     }
// }

// automatic generation
async function generateSummaryAutomatic(noteId) {
    try {
        const response = await fetch(`/summarize/${noteId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySummary(data.summary);
        } else {
            summaryDisplay.innerHTML = '<p class="error">Error generating summary</p>';
            summaryDisplay.style.display = 'block';
            summaryLoading.style.display = 'none';
        }
    } catch (error) {
        console.error('Error generating summary:', error);
        summaryDisplay.innerHTML = '<p class="error">Error generating summary</p>';
        summaryDisplay.style.display = 'block';
        summaryLoading.style.display = 'none';
    }
}

// manual from button
async function generateSummary() {
    const noteId = localStorage.getItem('currentNoteId');
    if (!noteId) {
        alert('Record something first!');
        return;
    }
    
    summaryLoading.style.display = 'flex';
    summaryDisplay.style.display = 'none';
    summaryActions.style.display = 'none';
    
    await generateSummaryAutomatic(noteId);
}

function displaySummary(summary) {
    if (summary && summary !== 'placeholder') {
        summaryDisplay.innerHTML = `
            <div class="summary-content">
                <h3>Summary</h3>
                <p>${escapeHtml(summary)}</p>
            </div>
        `;
    } else {
        summaryDisplay.innerHTML = '<p class="status">Summary pending...</p>';
    }
    
    summaryDisplay.style.display = 'block';
    summaryLoading.style.display = 'none';
    summaryActions.style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    const pendingSummary = sessionStorage.getItem('pendingSummary');
    if (pendingSummary) {
        displaySummary(pendingSummary);
        sessionStorage.removeItem('pendingSummary');
    }
});

