$(document).ready(function () {
    $('.delete-btn').on('click', function () {
        // 삭제하려는 게시물의 ID를 저장
        var postIdToDelete = $(this).data('post-id');
        $('#deleteModal').modal('show');
        $('#confirmDelete').data('post-id', postIdToDelete);
    });

    $('#confirmDelete').on('click', function () {
        var postID = $(this).data('post-id');
        $.ajax({
            url: '/delete_post/' + postID,
            type: 'POST',
            success: function (response) {
                $('#deleteModal').modal('hide'); // 모달 숨기기
                
                // 서버 요청이 성공한 후에 페이지 새로고침
                window.location.reload();
            },
            error: function (error) {
                console.log(error);
                alert('Error deleting post');
            }
        });
    });
});




