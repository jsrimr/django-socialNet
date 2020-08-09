from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView

from profiles.models import Profile
from .forms import PostModelForm, CommentModelForm
from .models import Post, Like


# Create your views here.
def post_comment_create_and_list_view(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)
    # Post form, comment form
    p_form = PostModelForm()
    c_form = CommentModelForm()
    p_form_submitted = False

    if 'submit_p_form' in request.POST:
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():  # 이건 왜 request.method==POST 일때만 하는게 안리까>
            instance = p_form.save(commit=False)  # problem => author 가 필요
            instance.author = profile
            instance.save()
            p_form_submitted = True
            p_form = PostModelForm()

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST, request.FILES)
        if request.method == "POST":
            if c_form.is_valid():
                instance = c_form.save(commit=False)
                instance.user = profile
                instance.post = Post.objects.get(id=request.POST.get('post_id'))
                instance.save()
                c_form = CommentModelForm()

    context = {
        'qs': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'p_form_submitted': p_form_submitted,
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

        like, created = Like.objects.get_or_create(user=profile,
                                                   post_id=post_id)  # get_or_create : 있으면 가져오고 없으면 더미 만들어서 가져온다

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Like'

        post_obj.save()
        like.save()

    return redirect('posts:main-post-view')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/confirm_del.html'
    success_url = reverse_lazy('posts:main-post-view')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'You need to be the authr')
        return obj


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostModelForm
    template_name = 'posts/update.html'
    success_url = reverse_lazy('posts:main-post-view')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, "You need to be auth to Update")
            return super().form_invalid(form)
