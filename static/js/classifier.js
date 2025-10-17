let sendCommentBtn;
let positiveFeedbackBtn;
let negativeFeedbackBtn;

function sendData(comment) {
    if (!comment) {
        return;
    }

    sendCommentBtn.classList.add('disabled');

    const formData = new FormData();
    formData.append('text', comment);

    fetch('/classify/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        showResult(data.is_toxic, data.probability);
        updaterFeedbackData(comment, data.is_toxic);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showError('Произошла ошибка при анализе комментария');
    }).finally(() => {
        sendCommentBtn.classList.remove('disabled');
    });
}


function getFeedbackBlock() {
    return document.getElementById('feedback-block');
}


function hideFeedbackBlock() {
    const feedbackBlock = getFeedbackBlock();
    feedbackBlock.classList.add('d-none');
}


function updaterFeedbackData(text, isToxic) {
    const feedbackBlock = getFeedbackBlock();
    feedbackBlock.classList.remove('d-none');
    feedbackBlock.dataset.commentData = JSON.stringify({text, isToxic});
}


function getResultBlock() {
    return document.getElementById('result-block');
}


function showResult(isToxic, probability) {
    const resultBlock = getResultBlock();
    resultBlock.innerHTML = isToxic ?
        `<span>Комментарий <span class="text-danger fw-bold">ТОКСИЧНЫЙ</span> (${probability})</span>` :
        `<span>Комментарий <span class="text-success fw-bold">не токсичный</span> (${probability})</span>`;
}

function showError() {
    const resultBlock = getResultBlock();
    resultBlock.innerHTML = `<span class="text-danger fw-bold">Серверная ошибка</span>`
}


function sendComment() {
    const comment = document.getElementById('comment-field');
    sendData(comment.value);
}


function disableFeedbackButtons(disable) {
    const value = disable ? 'none' : 'auto';
    negativeFeedbackBtn.style.pointerEvents = value;
    positiveFeedbackBtn.style.pointerEvents = value;
}


function setFeedbackProgress(text) {
    document.getElementById('feedback-progress').innerText = text;
}


function sendFeedback() {
    disableFeedbackButtons(true);
    setFeedbackProgress('Отправлю данные....');

    const feedbackBlock = getFeedbackBlock();
    const commentData = JSON.parse(feedbackBlock.dataset.commentData);

    const formData = new FormData();
    formData.append('text', commentData.text);
    // Инвертируем значение, так как фидбек отправляем только отрицательный.
    // Если изначально коммент определился как токсичный, то отправляем как нетоксичный
    formData.append('is_toxic', commentData.isToxic ? '0' : '1');

    fetch('/fit/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        hideFeedbackBlock();
    })
    .catch(error => {
        console.error('Ошибка:', error);
    }).finally(() => {
        disableFeedbackButtons(false);
        setFeedbackProgress('');
    });
}


document.addEventListener("DOMContentLoaded", function() {
  sendCommentBtn = document.getElementById('check-comment-btn');
  sendCommentBtn.addEventListener('click', sendComment);

  positiveFeedbackBtn = document.getElementById('positive-feedback-btn');
  positiveFeedbackBtn.addEventListener('click', hideFeedbackBlock);

  negativeFeedbackBtn = document.getElementById('negative-feedback-btn');
  negativeFeedbackBtn.addEventListener('click', sendFeedback);
});
