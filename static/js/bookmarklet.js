// var redirect_base = "http://127.0.0.1:8080/api/"
var redirect_base = "http://flickr2tag.drikin.com/api/"

var jscript = document.createElement('script');
jscript.setAttribute('src', 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js');
document.getElementsByTagName('body')[0].appendChild(jscript);

var src=location.href;
var re_flickr_user = /http:\/\/www.flickr.com\/photos\/.+\//;
var re_flickr_group = /http:\/\/www.flickr.com\/groups\/.+\//;

if (src.match(re_flickr_user)) {
	window.location.href = redirect_base + "redirectuser?src=" + src
} else if (src.match(re_flickr_group)){
	window.location.href = redirect_base + "redirectgroup?src=" + src
} else {
	window.location.href = "http://flickr2tag.drikin.com/"
}