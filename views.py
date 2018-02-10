from django.core.paginator import ( EmptyPage, PageNotAnInteger, Paginator)
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.views.generic import ( CreateView, DeleteView, DetailView, ListView)
from .forms import TagForm, POCForm, NewsLinkForm
from .models import Tag, POC, NewsLink
from .utils import ObjectCreateMixin, ObjectUpdateMixin, ObjectDeleteMixin, POCContextMixin
from .utils import PageLinksMixin, NutDataContextMixin, POCContextMixin, NewsLinkGetObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.template import Context, loader
from core.utils import UpdateView
from user.decorators import class_login_required, require_authenticated_permission
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
#mport requests
from django.core.paginator import Paginator
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
import cloudinary
import cloudinary.uploader
import cloudinary.api
import unicodedata
import logging
import django_filters
from .filters import POCFilter
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator

def search(request):
    #oc_list = POC.objects.all()
    query = request.GET.get('q')
    try:
      print ('77a: ',query)
      poc_list = POC.objects.filter(id=int(query))
      print ('77b')
    except:
      print ('77c')
      #oc_list = POC.objects.filter(name__contains=query)
      try:
        poc_list = POC.objects.filter(name__icontains=query)
      except:
        poc_list = POC.objects.filter(slug__icontains=query)
    print ('77d')
    return render(request, 'nutr/poc_list.html', {'poc_list': poc_list})

class POCList(PageLinksMixin, ListView):
    model = POC
    paginate_by = 30


def poc_detail(request, slug):
    poc = get_object_or_404(
        POC, slug=slug)
    name=poc.name
    clone3=strip_accents3(name)
    #pg_url="http://res.cloudinary.com/hh9sjfv1s/image/upload/v1509393104/"+clone3+".jpg"
    # 10/31/17 discovered (cloudinary docs weren't much help) you don't need the version number:
    jpg_url="http://res.cloudinary.com/hh9sjfv1s/image/upload/"+clone3+".jpg"
    jpg_url=jpg_url.replace(' ','_')
    logging.debug('(51p) jpg_url: ',jpg_url)
    return render(
        request,
        'nutr/poc_detail.html',
        {'poc': poc ,
        'jpg_url':jpg_url,
	#poc.image': poc.image.url
        })

def homepage(request):
    #or header in request.META:
      #rint('55d header: ',header,':',request.META[header])
    #eturn render( request, 'nutr/tag_list.html', {'tag_list': Tag.objects.all()})
    response = render( request, 'nutr/tag_list.html', {'tag_list': Tag.objects.all()})
    return response

TAG_KEY="tag"
ALL_POC_KEY="all_poc"
TAG=''
#cache_page(60 * 15)
def tag_detail(request, slug):
    AMOUNT_LISTED_POC = 100 
    #ESSION_KEY=request.session._get_or_create_session_key()
    #rint("tag_detail SESSION_KEY: ",SESSION_KEY)
    #ogging.debug("tag_detail SESSION_KEY: ",SESSION_KEY)
    #ag=cache.get(TAG_KEY+TAG)
    #ll_poc=cache.get(ALL_POC_KEY+TAG)
    #f not tag or not all_poc:
    if True:
      tag = get_object_or_404( Tag, slug__iexact=slug)
      #AG=tag
      all_poc = tag.poc_set.all().order_by('name')
      #rint("63u (print) tag_name: ",tag.name)
      #ache.set(TAG_KEY+TAG,tag)
      #ache.set(ALL_POC+TAG,all_poc)
    else:
      print("63b tag_detail caching is working!!")
    page = request.GET.get("page",1)
    if page:
        paginator = Paginator(all_poc,AMOUNT_LISTED_POC)
        try:
            all_poc = paginator.page(page)
        except PageNotAnInteger:
            all_poc = paginator.page(1)
        except EmptyPage:
            all_poc = paginator.page(paginator.num_pages)

    return render(
        request,
        'nutr/tag_detail.html',
        {'tag': tag, 'all_poc':all_poc})

def image(request, jpg):
    #eturn HttpResponse(jpg)
    return render(
        request,
        jpg,
        {})

TAG_LIST_KEY = "tag_list"
#cache_page(60 * 15)
def tag_list(request):
  #or header in request.META:
    #rint('55f request header: ',header,':',request.META[header])
  #ESSION_KEY=request.session._get_or_create_session_key()
  #rint("tag_list SESSION_KEY: ",SESSION_KEY)
  #ogging.debug("tag_list SESSION_KEY: ",SESSION_KEY)
  #ag_list=cache.get(TAG_LIST_KEY)
  #f not tag_list:
  if True:
    tag_list = Tag.objects.all()
    #rint("63t not tag (print): ",type(tag_list))
    logging.debug("63t not tag (debug): ",type(tag_list))
    #ache.set(TAG_LIST_KEY, tag_list)
  else:
    print("63a tag_list caching is working!! (print)")
    debug.logging("63a tag_list caching is working!! (debug)")

  c = {'tag_list': tag_list}
  #.update(csrf(request))
  return render_to_response('nutr/tag_list.html', c)


def poc_create(request):
    if request.method == 'POST':
        form = POCForm(request.POST)
        if form.is_valid():
            new_poc = form.save()
            return redirect(new_poc)
    else:  # request.method != 'POST'
        form = POCForm()
    return render(
        request,
        'nutr/poc_form.html',
        {'form': form})

class POCCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    form_class = POCForm
    template_name = 'nutr/poc_form.html'

@require_authenticated_permission( 'nutr.create_tag')
class TagCreate(ObjectCreateMixin, View):
    form_class = TagForm
    template_name = 'nutr/tag_form.html'

@require_authenticated_permission( 'nutr.update_tag')
class TagUpdate(ObjectUpdateMixin, View):
    form_class = TagForm
    model = Tag
    template_name = (
        'nutr/tag_form_update.html')

@require_authenticated_permission( 'nutr.delete_tag')
class TagDelete(ObjectDeleteMixin, View):
    model = Tag
    success_url = reverse_lazy(
        'nutr_tag_list')
    template_name = (
        'nutr/tag_confirm_delete.html')

#require_authenticated_permission( 'nutr.update_poc')
class POCUpdate(LoginRequiredMixin,ObjectUpdateMixin, View):
    form_class = POCForm
    model = POC
    template_name = ( 'nutr/poc_form_update.html')

#require_authenticated_permission( 'nutr.delete_poc')
class POCDelete(ObjectDeleteMixin, View):
    model = POC
    success_url = reverse_lazy(
        'nutr_tag_list')
    template_name = (
        'nutr/poc_confirm_delete.html')

class NewsLinkCreate(
        NewsLinkGetObjectMixin,
        POCContextMixin,
        CreateView):
    form_class = NewsLinkForm
    model = NewsLink

    def get_initial(self):
        poc_slug = self.kwargs.get(
            self.poc_slug_url_kwarg)
        self.poc = get_object_or_404(
            POC, slug__iexact=poc_slug)
        initial = {
            self.poc_context_object_name:
                self.poc,
        }
        initial.update(self.initial)
        return initial

@require_authenticated_permission( 'nutr.delete_newslink')
class NewsLinkDelete(
        NewsLinkGetObjectMixin,
        POCContextMixin,
        DeleteView):
    model = NewsLink
    slug_url_kwarg = 'newslink_slug'

    def get_success_url(self):
        return (self.object.poc
                .get_absolute_url())


@require_authenticated_permission( 'nutr.update_newslink')
class NewsLinkUpdate(
        NewsLinkGetObjectMixin,
        POCContextMixin,
        UpdateView):
    form_class = NewsLinkForm
    model = NewsLink
    slug_url_kwarg = 'newslink_slug'


def upload(request):
    logging.debug('upload() (21)')
    #f request.method == 'POST' and request.FILES['myfile']:
    if request.method == 'POST':
        print('upload() (22d) - type(request.FILES): ',type(request.FILES))
        print('upload() (22i) - request.FILES: ',request.FILES)
        print('upload() (22m) - request.FILES.__dict__: ',request.FILES.__dict__)
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        logging.debug('upload() (26)')
        filename = fs.save(myfile.name, myfile)
        url=fs.url(myfile.name)
        uploaded_file_url = fs.url(filename)
        logging.debug('upload() (27a) - myfile.fileno: ',str(myfile.fileno))
        #rint('upload() (27b) - myfile.seek(): ',str(myfile.seek()))
        #rint('upload() (27c) - myfile.tell(): ',str(myfile.tell()))
        print('upload() (27d) - myfile._get_name: ',str(myfile._get_name))
        logging.debug('upload() (27e) - myfile.open(): ',str(myfile.open()))
        logging.debug('upload() (27f) - myfile.read(): ',str(myfile.read()))
        logging.debug('upload() (27g) - myfile.size: ',str(myfile.size)) #222k
        logging.debug('upload() (27h) - filename: ',filename) 
        logging.debug('upload() (27i) - url: ',url) 
        print('upload() (27i) - url: ',url) 
        #rint("upload() (27j) - form.cleaned_data['name']: ",form.cleaned_data['name'])
        logging.debug("upload() (27k) - dir(request): ",dir(request))
        #eturned=cloudinary.uploader.upload('/Users/michaelsweeney/Christmas_card.jpg')
        #eturned=cloudinary.uploader.upload(filename,use_filename=True,unique_filename=False)
        returned=cloudinary.uploader.destroy(url)
        for k, v in returned.items():
            print('upload() (27o) - returned dict has: ',k, v)
        returned=cloudinary.uploader.upload(url,use_filename=True,unique_filename=False,invalidate=True,overwrite=True,version=True)
        for k, v in returned.items():
            print('upload() (27p) - returned dict has: ',k, v)
        """"
        returned dict has:  secure_url https://res.cloudinary.com/hh9sjfv1s/image/upload/v1503348883/whnqvmv2smbec9s8zq15.jpg
        returned dict has:  url        http://res.cloudinary.com/hh9sjfv1s/image/upload/v1503348883/whnqvmv2smbec9s8zq15.jpg
        """
        return render(request, 'nutr/poc_image_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    logging.debug('upload() (28m)')
    return render(request, 'nutr/poc_image_upload.html')


def upload_broke(request):
    logging.debug('upload() (21)')
    #f request.method == 'POST' and request.FILES['myfile']:
    if request.method == 'POST':
        logging.debug('upload() (22)')
        try:
            myfile = request.FILES['myfile']
        except Exception as ex:
            logging.debug("Unexpected error:", ex)
        logging.debug('upload() (24)')
        fs = FileSystemStorage()
        logging.debug('upload() (26a)')
        filename = fs.save(myfile.name, myfile)
        logging.debug('upload() (26b)')
        url=fs.url(myfile.name)
        logging.debug('upload() (26d)')
        #ploaded_file_url = fs.url(filename)
        logging.debug('upload() (27a) - myfile.fileno: ',str(myfile.fileno))
        #rint('upload() (27b) - myfile.seek(): ',str(myfile.seek()))
        #rint('upload() (27c) - myfile.tell(): ',str(myfile.tell()))
        logging.debug('upload() (27d) - myfile._get_name: ',str(myfile._get_name))
        logging.debug('upload() (27e) - myfile.open(): ',str(myfile.open()))
        logging.debug('upload() (27f) - myfile.read(): ',str(myfile.read()))
        logging.debug('upload() (27g) - myfile.size: ',str(myfile.size)) #222k
        #rint('upload() (27h) - filename: ',filename) 
        logging.debug('upload() (27i) - url: ',url) 
        #rint("upload() (27j) - form.cleaned_data['name']: ",form.cleaned_data['name'])
        logging.debug("upload() (27k) - dir(request): ",dir(request))
        logging.debug("upload() (27l) - dir(myfile): ",dir(myfile))
        logging.debug("upload() (27n) - myfile.name: ",myfile.name)
        logging.debug("upload() (27o) - myfile.file: ",myfile.file)
        #eturned=cloudinary.uploader.upload('/Users/michaelsweeney/Christmas_card.jpg')
        #eturned=cloudinary.uploader.upload(filename,use_filename=True,unique_filename=False)
        try:
            returned=cloudinary.uploader.upload(myfile.name,use_filename=True,unique_filename=False)
            for k, v in returned.items():
                logging.debug ('returned dict has: ',k, v)
        except Exception as ex:
            logging.debug("Unexpected error:", ex)
        #eturn render(request, 'nutr/poc_image_upload.html', {
            #uploaded_file_url': uploaded_file_url
        #)
    logging.debug('upload() (28m)')
    return render(request, 'nutr/poc_image_upload.html')

def upload_do(request,slug):
    logging.debug('upload_do() (2)')
    return HttpResponse()

def simple_upload(request):
    logging.debug('simple_upload() (1)')
    if request.method == 'POST' and request.FILES['myfile']:

        logging.debug('simple_upload() (2)')
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        logging.debug('simple_upload() (6)')
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        logging.debug('simple_upload() (9)')
        return render(request, 'core/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'nutr/tag_list.html')


def model_form_upload(request):
    logging.debug('model_form_upload() (1)')
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    })

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'

def strip_accents3(input_str):
	s = ''
	#rint input_str.encode('utf-8')
	for c in input_str:
		if c in s1:
			s += s0[s1.index(c)]
		else:
			s += c
	return s
