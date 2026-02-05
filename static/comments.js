async function initComments() {
    // Boss send comment
    const commentInput = document.getElementById('bossComment');
    const departmentSelect = document.getElementById('departmentSelect');
    const commentButton = document.getElementById('bossCommentSubmit');

    if (commentButton) {
        commentButton.addEventListener('click', async () => {
            const department = departmentSelect?.value;
            const message = commentInput?.value;

            if (!department) {
                alert('Please select a department');
                return;
            }

            if (!message.trim()) {
                alert('Please enter a message');
                return;
            }

            try {
                const response = await fetch('/api/comments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        department: department,
                        message: message
                    })
                });

                if (response.ok) {
                    alert('Message sent successfully!');
                    commentInput.value = '';
                    departmentSelect.value = '';
                } else {
                    alert('Failed to send message');
                }
            } catch (err) {
                console.error('Error sending comment:', err);
                alert('Error sending message');
            }
        });
    }

    // Load comments for non-boss users
    const commentsDisplay = document.getElementById('departmentComments');
    if (commentsDisplay) {
        await loadComments(commentsDisplay);
    }
}

async function loadComments(commentsDisplay) {
    try {
        const response = await fetch('/api/comments');
        const data = await response.json();

        if (data.comments && data.comments.length > 0) {
            let html = '';
            data.comments.forEach((comment, index) => {
                html += `
                    <div class="comment-item" id="comment-${index}">
                        <div class="comment-item-row">
                            <div>
                                <div class="sender">📌 From: ${comment.sender}</div>
                                <div class="content">${comment.content}</div>
                                <div class="timestamp">${comment.timestamp}</div>
                            </div>
                            <button class="mark-read-btn" onclick="markAsRead(${index})">Mark as Read</button>
                        </div>
                    </div>
                `;
            });
            commentsDisplay.innerHTML = html;
        } else {
            commentsDisplay.innerHTML = '<p class="no-comments">No messages yet</p>';
        }
    } catch (err) {
        console.error('Error loading comments:', err);
        commentsDisplay.innerHTML = '<p class="no-comments">Error loading messages</p>';
    }
}

async function markAsRead(index) {
    try {
        const response = await fetch('/api/comments', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                index: index
            })
        });

        if (response.ok) {
            const commentElement = document.getElementById(`comment-${index}`);
            if (commentElement) {
                commentElement.remove();
            }

            const commentsDisplay = document.getElementById('departmentComments');
            if (commentsDisplay && commentsDisplay.children.length === 0) {
                commentsDisplay.innerHTML = '<p class="no-comments">No messages yet</p>';
            }
        } else {
            alert('Failed to mark as read');
        }
    } catch (err) {
        console.error('Error marking as read:', err);
        alert('Error marking as read');
    }
}

document.addEventListener('DOMContentLoaded', initComments);
