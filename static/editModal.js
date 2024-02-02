$(document).ready(function () {
    $('.edit-btn').on('click', function () {
        var postId = $(this).data('post-id'); // 'data-post-id' 속성을 통해 게시물 ID를 가져옵니다.
        // AJAX를 통해 서버에서 해당 게시물 정보를 가져옵니다.
        $.get('/get-post-info/' + postId, function (postData) {
            $('#editPostID').val(postData.postID);
            // $('#editUserID').val(postData.userID);
            $('#editTypeSelect').val(postData.type);
            $('#editTitle').val(postData.title);
            $('#editImageUrl').val(postData.image_url);
            $('#editContent').val(postData.content);
            $('#editUrl').val(postData.url);
        });
    });

    $('#editForm').on('submit', function (e) {
        e.preventDefault();
        var postId = $('#editPostID').val();
        var data = {
            userID: $('#editUserID').val(),
            type: $('#editTypeSelect').val(),
            title: $('#editTitle').val(),
            image_url: $('#editImageUrl').val(),
            content: $('#editContent').val(),
            url: $('#editUrl').val()
        };
        $.ajax({
            url: '/edit-post/' + postId,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (result) {
                // UI 업데이트, 예를 들어 페이지 새로고침 없이 변경된 정보를 표시
                $('#editModal').modal('hide'); // 모달 닫기
                // 변경된 게시물 정보를 페이지에 반영하는 로직을 추가할 수 있습니다.
                location.reload(); // 단순하게 페이지를 새로고침하여 변경사항 반영
            },
            error: function (error) {
                console.error('Error updating post: ', error);
                alert('게시물 수정 중 오류가 발생했습니다. 다시 시도해주세요.');
            }
        });
    });
});
