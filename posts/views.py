from django.shortcuts import render, redirect

from profiles.models import Profile
from .models import Post, Like


# Create your views here.
def post_comment_create_and_list_view(request):
    qs = Post.objects.all()

    context = {
        'qs': qs,
    }
    return render(request, 'posts/main.html', context)


def like_unlike_post(request):
    user = request.user
    if request.method == "POST":
        post_id = request.POST.get('post_id')  # 어떻게 request에서 원하는 변수를 얻어내는가!
        post_obj = Post.objects.get(id=post_id)  # 어떻게 db에서 원하는 트랜잭션을 가져오는가!
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)  # db 삭제 메소드
        else:
            post_obj.liked.add(profile)  # db 추가 메소드

        like, created = Like.objects.get_or_create(user=profile, post_id=post_id) # get_or_create : 있으면 가져오고 없으면 더미 만들어서 가져온다

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'

        post_obj.save()
        like.save()

    return redirect('posts:main-post-view')
