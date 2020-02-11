from django.shortcuts import render

# This file is used to display web pages

def main_page(request):
    return render(request, 'mainPage.html')

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'mainPage.html', {'form': form})