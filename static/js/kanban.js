/* ProjectFlow - Kanban Board Drag & Drop */

document.addEventListener('DOMContentLoaded', function() {
    var board = document.getElementById('kanban-board');
    if (!board) return;

    var boardType = board.getAttribute('data-board-type') || 'tasks';
    var moveUrl = boardType === 'issues' ? '/issues/kanban/move/' : '/tasks/kanban/move/';
    var idField = boardType === 'issues' ? 'issue_id' : 'task_id';

    var draggedCard = null;
    var originalParent = null;
    var originalNextSibling = null;

    document.querySelectorAll('.kanban-card').forEach(function(card) {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    document.querySelectorAll('.kanban-column-body').forEach(function(column) {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('dragenter', handleDragEnter);
        column.addEventListener('dragleave', handleDragLeave);
        column.addEventListener('drop', handleDrop);
    });

    function handleDragStart(e) {
        draggedCard = this;
        originalParent = this.parentElement;
        originalNextSibling = this.nextElementSibling;
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', this.getAttribute('data-item-id') || this.getAttribute('data-task-id'));
    }

    function handleDragEnd(e) {
        this.classList.remove('dragging');
        document.querySelectorAll('.kanban-column-body').forEach(function(col) {
            col.classList.remove('drag-over');
        });
        draggedCard = null;
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        var afterElement = getDragAfterElement(this, e.clientY);
        if (afterElement == null) {
            this.appendChild(draggedCard);
        } else {
            this.insertBefore(draggedCard, afterElement);
        }
    }

    function handleDragEnter(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    }

    function handleDragLeave(e) {
        if (!this.contains(e.relatedTarget)) {
            this.classList.remove('drag-over');
        }
    }

    function handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drag-over');

        var itemId = e.dataTransfer.getData('text/plain');
        var newStatus = this.getAttribute('data-status');
        var movedCard = draggedCard;
        var previousStatus = movedCard ? movedCard.getAttribute('data-status') : newStatus;

        var cards = Array.from(this.querySelectorAll('.kanban-card'));
        var order = cards.indexOf(movedCard);

        if (movedCard) {
            movedCard.setAttribute('data-status', newStatus);
        }

        updateColumnCounts();

        var payload = {
            status: newStatus,
            order: order,
        };
        payload[idField] = parseInt(itemId);

        if (movedCard) movedCard.classList.add('is-saving');

        fetch(moveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(payload),
        })
        .then(function(r) {
            return r.json().then(function(data) {
                if (!r.ok) throw new Error(data.error || 'Could not save move');
                return data;
            });
        })
        .then(function(data) {
            if (!data.success) {
                throw new Error(data.error || 'Could not save move');
            }
        })
        .catch(function(err) {
            console.error('Network error:', err);
            if (movedCard && originalParent) {
                movedCard.setAttribute('data-status', previousStatus);
                originalParent.insertBefore(movedCard, originalNextSibling);
                updateColumnCounts();
            }
        })
        .finally(function() {
            if (movedCard) movedCard.classList.remove('is-saving');
        });
    }

    function getDragAfterElement(container, y) {
        var draggableElements = Array.from(
            container.querySelectorAll('.kanban-card:not(.dragging)')
        );

        return draggableElements.reduce(function(closest, child) {
            var box = child.getBoundingClientRect();
            var offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    function updateColumnCounts() {
        document.querySelectorAll('.kanban-column').forEach(function(column) {
            var count = column.querySelector('.kanban-column-body').querySelectorAll('.kanban-card').length;
            var countEl = column.querySelector('.kanban-column-count');
            if (countEl) {
                countEl.textContent = count;
            }
        });
    }

    function getCsrfToken() {
        var cookie = document.cookie.split(';').find(function(c) {
            return c.trim().startsWith('csrftoken=');
        });
        return cookie ? cookie.split('=')[1] : '';
    }
});
